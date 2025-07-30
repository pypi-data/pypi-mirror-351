import logging
from collections.abc import Iterable
from inspect import getfullargspec

import tensorflow as tf
from elvet.models import nn
from elvet.system.exceptions import (
    InvalidDataType,
    InvalidDomain,
    InvalidHypothesis
)

log = logging.getLogger("Elvet")


class _MinimizerInputNormalizer:
    """
    Normalizes user input.

    The arguments of the constructor are the arguments to `minimizer`.

    The attributes are the arguments of the `Minimizer` constructor.
    """

    _optimizer_keys = [
        "learning_rate",
        "lr",
        "decay",
        "beta_1",
        "beta_2",
        "momentum",
        "rho",
        " learning_rate_power",
        "l1_regularization_strength",
        "l2_regularization_strength",
        "beta",
    ]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, f"_{key}", value)

        optimizer_params = kwargs.get("optimizer_params", {})
        self._optimizer_params = {}
        for key, value in optimizer_params.items():
            if key not in _MinimizerInputNormalizer._optimizer_keys:
                log.warning(f"Invalid optimizer input : {key}. Input will be ignored.")
            else:
                if key == "lr":
                    self._optimizer_params["learning_rate"] = value
                else:
                    self._optimizer_params[key] = value

        if kwargs.get("validate_model", True):
            self.validate_model()

    @property
    def functional(self):
        return _MinimizerInputNormalizer.normalize_functional(
            self._functional,
            self._batch,
        )

    @property
    def domain(self):
        try:
            return tf.convert_to_tensor(self._domain, dtype=self._dtype)
        except ValueError as err:
            raise InvalidDomain(str(err))

    @property
    def order(self):
        return (
            self._order
            if self._order is not None
            else (len(getfullargspec(self._functional).args) - 2)
        )

    @property
    def combinator(self):
        return (lambda x: x) if self._combinator is None else self._combinator

    @property
    def model(self):
        return nn(1, 10, 1) if self._model is None else self._model

    @property
    def optimizer(self):
        optimizers = {
            tf.keras.optimizers.Adam,
            tf.keras.optimizers.SGD,
            tf.keras.optimizers.RMSprop,
            tf.keras.optimizers.Adadelta,
            tf.keras.optimizers.AdamW,
            tf.keras.optimizers.Adagrad,
            tf.keras.optimizers.Adamax,
            tf.keras.optimizers.Adafactor,
            tf.keras.optimizers.Nadam,
            tf.keras.optimizers.Ftrl,
            tf.keras.optimizers.Lion,
            tf.keras.optimizers.LossScaleOptimizer,
        }
        optimizers_dict = {cls.__name__.lower(): cls for cls in optimizers}
        return optimizers_dict[self._optimizer.lower()](**self._optimizer_params)

    @property
    def callbacks(self):
        if self._callbacks is None:
            return []
        elif isinstance(self._callbacks, Iterable):
            return list(self._callbacks)
        else:
            return [self._callbacks]

    @property
    def metrics(self):
        if self._metrics is None:
            return []
        elif isinstance(self._metrics, Iterable):
            return list(self._metrics)
        else:
            return [self._metrics]

    def validate_model(self):
        if not hasattr(self.model, "trainable_variables"):
            raise InvalidHypothesis()

        if not hasattr(self.model, "input"):
            log.warning("Model does not have input instance.")

        elif tf.as_dtype(self.model.input.dtype) is not self.domain.dtype:
            raise InvalidDataType(
                "Invalid data type! " "Hypothesis data type is different from domain."
            )

    @staticmethod
    def normalize_functional(functional, batch):
        """
        Standardize functional to always take domain and *derivatives as
        arguments in batched form.
        """

        if len(getfullargspec(functional).args) == 0:

            def _functional(domain, *derivatives):
                return functional()

            functional = _functional

        if batch:
            return functional

        def tupled_functional(args):
            domain, derivatives = args
            return functional(domain, *derivatives)

        def batched_functional(domain, *derivatives):
            return tf.vectorized_map(tupled_functional, (domain, derivatives))

        return batched_functional
