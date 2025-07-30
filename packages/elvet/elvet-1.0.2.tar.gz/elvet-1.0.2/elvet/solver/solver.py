import logging

import tensorflow as tf

from elvet.minimizer.minimizer import Minimizer
from elvet.solver._input_normalizer import _SolverInputNormalizer

log = logging.getLogger("Elvet")


def solver(
    equations,
    bcs,
    domain,
    order=None,
    combinator=None,
    batch=False,
    model=None,
    dtype=tf.float32,
    optimizer="adam",
    callbacks=None,
    metrics=None,
    epochs=None,
    verbose=True,
    **optimizer_params,
):
    """
    Frontend for solving differential equations. The differential equations and
    boundary conditions can always be written in the form

    .. math::
        {\\rm equations} \\left(
            x_i,
            \\frac{\\partial}{\\partial x_i} y_j,
            \\frac{\\partial^2}{\\partial x_i \\partial x_j} y_k,
            \\ldots
        \\right) = 0,

    .. math::
        {\\rm bcs} \\left(
            x_i,
            \\frac{\\partial}{\\partial x_i} y_j,
            \\frac{\\partial^2}{\\partial x_i \\partial x_j} y_k,
            \\ldots
        \\right) = 0.

    The functions ``equations`` and ``bcs`` defined in this way are to be passed as
    arguments to ``solver``. ``equations`` can return a list or a tuple in the case
    of a system of differential equations. The argument ``bcs`` can be a simple function
    or an instance of ``elvet.BC`` in the case of a single boundary condition. If there
    are several boundary conditions, a list or tuple can be passed as the ``bcs``
    argument.

    The specification for the arguments of ``equations`` and ``bcs`` in the default
    non-batch mode is::

        def equations(x, y, dy, d2y, d3y, ...):
            assert len(x.shape) == len(y.shape) == 1
            assert len(d3y.shape) == 1 + len(d2y.shape) == 2 + len(dy.shape) == 4

            dim_x, dim_y = x.shape[0], y.shape[0]

            assert dy.shape == (dim_x, dim_y)
            assert d2y.shape == (dim_x, dim_x, dim_y)
            assert d3y.shape == (dim_x, dim_x, dim_x, dim_y)

            # dy[i, j] = d_i y_j
            # d2y[i, j, k] = d_ij y_k
            # d3y[i, j, k, l] = d_ijk y_l

    where ``d_ij...``. means higher-order partial derivative with respect to :math:`x_i`
    , :math:`x_j` , ...:

    .. math::
        d_{ij\\ldots} = \\partial_i \\partial_j \\ldots
        = \\frac{\\partial^N}{\\partial x_i \\partial x_j \\ldots}

    (See the ``minimizer`` documentation for the batch mode specification)

    Parameters
    ----------
    equations : callable
        ``equations(domain, *derivatives)`` returning tf.Tensor or list or tuple

    bcs : elvet.BC or callable or list of elvet.BCs or callables
        boundary conditions ``bcs(domain, *derivatives)``

    domain : numpy.array or tf.Tensor or tf.Variable
        N dimensional input values as a column vector. ``x.shape = (M, N)`` where
        M is number of examples and N is number of dimensions.
        Hence one dimensional vector with 100 examples should look like
        ``x.shape = (100, 1)``

    combinator : callable, optional
        A method to combine equations and boundary conditions, the
        default is dennsolver.utils.loss_combinators.weighted_sum_combinator

    order : int, optional
        Order of the differential equation. If provided, the boundary
        condition checks will be overwritten.

    batch : bool, default=False
        If False, ``equations`` and ``bcs`` receive a point in the domain and the values
        of the functions and derivatives at this point. Otherwise, they receive
        "batches" consisting of all the points in the domain and the values of functions
        and derivatives at those points.

    model : elvet.nn or tf.keras.Model or tf.keras.Sequential, optional
        A trainable tensorflow model to represent the solution to the equation.

    dtype : tf.dtypes.DType, optional
        dtype of the domain/input of the model.

    optimizer : str or tensorflow optimizer, optional
        Defining the optimizer to be used, adam by default.

    callbacks : list, optional
        These are methods which can interfere with the algorithm where it
        can include LRschedulers or loss monitoring. They take a ``Solver`` object
        and return a ``bool``, which is true if the run is to be terminated early.

    metrics : list, optional
        These are the tools to monitor the parameters during the fitting.
        They receive a ``Solver`` object and return a dictionary with the names of
        the metrics as keys and their values. These values will be logged.

    epochs : int, optional
        If provided, the models is trained for the given number of epochs.

    verbose: bool, default=False
        If ``epochs`` is provided, whether to print metrics and epoch information while
        training.

    **optimizer_params
        Any optimizer-related input depending on the optimizer choosen by the
        user i.e. lr, decay, beta_1, beta_2, etc.

    Returns
    -------
    elvet.Solver
    """

    normalizer = _SolverInputNormalizer(
        equations=equations,
        bcs=bcs,
        domain=domain,
        order=order,
        combinator=combinator,
        batch=batch,
        model=model,
        dtype=dtype,
        optimizer=optimizer,
        callbacks=callbacks,
        metrics=metrics,
        epochs=epochs,
        verbose=verbose,
        optimizer_params=optimizer_params,
    )

    solver_obj = Solver(
        equations=normalizer.equations,
        bcs=normalizer.bcs,
        domain=normalizer.domain,
        order=normalizer.order,
        combinator=normalizer.combinator,
        model=normalizer.model,
        optimizer=normalizer.optimizer,
        callbacks=normalizer.callbacks,
        metrics=normalizer.metrics,
    )

    if epochs is not None:
        solver_obj.fit(epochs, verbose=verbose)

    return solver_obj


class Solver(Minimizer):
    """
    Differential equation solver.

    ``Solver`` objects are to be constructed using the ``solver`` function.

    Attributes
    ----------
    equations : callable
        ``equations(domain, *derivatives)`` returning ``tf.Tensor`` or list or tuple

    bcs : ``elvet.BC`` or callable or list of ``elvet.BC`` s or callables
        boundary conditions ``bcs(domain, *derivatives)``

    domain : tf.Tensor
        N dimensional input values as a column vector. ``x.shape = (M, N)`` where
        M is number of examples and N is number of dimensions.
        Hence one dimensional vector with 100 examples should look like
        ``x.shape = (100, 1)``

    combinator : callable
        A method to combine equations and boundary conditions.

    order : int
        Order of the differential equation.

    model : elvet.nn or tf.keras.Model or tf.keras.Sequential, optional
        A trainable tensorflow model representing the solution to the equation.

    optimizer : tensorflow optimizer
        The optimizer to be used to train the model.

    callbacks : list
        These are methods which can interfere with the algorithm where it
        can include LRschedulers or loss monitoring. They take a ``Solver`` object
        and return a ``bool``, which is true if the run is to be terminated early.

    metrics : list
        These are the tools to monitor the parameters during the fitting.
        They receive a ``Solver`` object and return a dictionary with the names of
        the metrics as keys and their values. These values will be logged.
    """

    def __init__(
        self,
        equations,
        bcs,
        domain,
        order,
        combinator,
        model,
        optimizer,
        callbacks,
        metrics,
    ):
        self.equations = equations
        self.bcs = bcs

        def functional(domain, *derivatives):
            return (
                equations(domain, *derivatives),
                tuple(bc(domain, *derivatives) for bc in bcs),
            )

        super().__init__(
            functional=functional,
            domain=domain,
            order=order,
            combinator=combinator,
            model=model,
            optimizer=optimizer,
            callbacks=callbacks,
            metrics=metrics,
        )

    def loss_density(self, domain=None):
        """
        The loss density is the contribution to the loss from each point in the domain.
        This is a very useful observable to assess the quality of the fit.

        Parameters
        ----------
        domain : tf.Tensor, optional
            to compute the loss density over, instead of ``self.domain``

        Returns
        -------
        np.array
        """

        if domain is None:
            domain = self.domain

        derivatives = self.derivatives(domain=domain)

        # Syntax of the equation changes in the non-batch mode,
        # hence it should be calculated accordingly.
        loss_eqs, loss_bcs = self.functional(domain, *derivatives)

        loss_eqs = sum(eq ** 2 for eq in loss_eqs)
        loss_bcs = sum(bc ** 2 for bc in loss_bcs)

        return loss_eqs.numpy().flatten() + loss_bcs.numpy().flatten()
