from collections.abc import Iterable
from inspect import getfullargspec
import logging

import tensorflow as tf

from elvet.utils.loss_combinators import weighted_sum_combinator
from elvet.minimizer._input_normalizer import _MinimizerInputNormalizer
from elvet.system.exceptions import InvalidBound, InvalidEquation


log = logging.getLogger("Elvet")


class _SolverInputNormalizer(_MinimizerInputNormalizer):
    """
    Normalizes user input.

    The arguments of the constructor are the arguments to `solver`.

    The attributes are the arguments of the `Solver` constructor.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if kwargs.get("order", None) is None:
            self.check_number_bcs()

    @property
    def equations(self):
        """
        Standardize equations to always take domain and *derivatives as
        arguments and return an iterable of tensors.
        """

        if not hasattr(self._equations, "__call__"):
            raise InvalidEquation("Invalid equation: it has to be callable.")

        equations = _MinimizerInputNormalizer.normalize_functional(
            self._equations,
            self._batch,
        )

        def standardized_equations(*args):
            return_value = equations(*args)

            if _SolverInputNormalizer._non_tensor_iterable(return_value):
                return return_value
            else:
                return (return_value,)

        return standardized_equations

    @property
    def bcs(self):
        """
        Standardize bcs to always be a list of callables
        taking domain and *derivatives as arguments.
        """

        if _SolverInputNormalizer._non_tensor_iterable(self._bcs):
            bcs = self._bcs
        else:
            bcs = [self._bcs]

        return [
            _MinimizerInputNormalizer.normalize_functional(bc, self._batch)
            for bc in bcs
        ]

    @property
    def order(self):
        return (
            self._order
            if self._order is not None
            else (len(getfullargspec(self._equations).args) - 2)
        )

    @property
    def combinator(self):
        return weighted_sum_combinator if self._combinator is None else self._combinator

    def check_number_bcs(self):
        """
        Check the number of boundary conditions provided. In single
        dimensional equations, the number of boundary conditions needs to be
        the same as the order of the equation. For multi dimensional equations
        each dimention needs same order of boundary conditions.
        """

        domain_dimension = self.domain.shape[-1]
        correct = True

        # user may not provide a tuple or list of bcs
        if hasattr(self.bcs, "__len__"):
            if 0 < len(self.bcs) < self.order * domain_dimension:
                log.error(
                    f"Expected {self.order} boundary conditions for each "
                    f"dimension but found only {len(self.bcs)} BCs."
                )
                correct = False
        else:
            if 1 < self.order * domain_dimension or self.bcs is None:
                log.error(
                    f"Expected {self.order} boundary conditions for each "
                    f"dimention but found only 1 BC."
                )
                correct = False

        if not correct:
            log.error(
                "Please provide more BCs or overwrite boundary check via the"
                "order optional parameter"
            )
            raise InvalidBound()

    @staticmethod
    def _non_tensor_iterable(item):
        return isinstance(item, Iterable) and not isinstance(
            item, (tf.Tensor, tf.Variable)
        )

    def functional(self, domain, *derivatives):
        return (
            self.equations(domain, *derivatives),
            tuple(bc(domain, *derivatives) for bc in self.bcs),
        )
