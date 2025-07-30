import logging
import os
import time

import numpy as np
import tensorflow as tf

from elvet.math.derivative import derivative_stack
from elvet.minimizer._input_normalizer import _MinimizerInputNormalizer
from elvet.system.exceptions import InvalidMetric

log = logging.getLogger("Elvet")


def minimizer(
    functional,
    domain,
    order=None,
    combinator=None,
    batch=True,
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
    Frontend for solving a functional minimization problem. Minimizes the functional
    :math:`F(y)` of some function :math:`y` of :math:`x`. :math:`F` is to be specified
    as a python function ``functional`` taking as arguments the points :math:`x` in the
    domain of :math:`y`, and the derivatives

    .. math::
         \\partial_i \\partial_j \\ldots y_k
         = \\frac{\\partial^n}{\\partial_i\\partial_j\\ldots} y_k

    of :math:`y`. The specification of the arguments of ``functional`` in the default
    batch mode is::

        def functional(x, y, dy, d2y, d3y, ...):
            assert len(x.shape) == len(y.shape) == 2
            assert len(d3y.shape) == 1 + len(d2y.shape) == 2 + len(dy.shape) == 5
            assert x.shape[0] == y.shape[0] == dy.shape[0] == d2y.shape[0]

            batch_size, dim_x, dim_y = x.shape[0] x.shape[1], y.shape[1]

            assert dy.shape == (batch_size, dim_x, dim_y)
            assert d2y.shape == (batch_size, dim_x, dim_x, dim_y)
            assert d3y.shape == (batch_size, dim_x, dim_x, dim_x, dim_y)

            # dy[:, i, j] = d_i (y_j)
            # d2y[:, i, j, k] = d_ij y_k
            # d3y[:, i, j, k, l] = d_ijk y_l

    where ``d_ij..``. means higher-order partial derivative with respect to :math:`x_i`
    , :math:`x_j` , ...:

    .. math::
        d_{ij\\ldots} = \\partial_i \\partial_j \\ldots
        = \\frac{\\partial^N}{\\partial x_i \\partial x_j \\ldots}

    (See the ``solver`` documentation for the batch mode specification)

    Parameters
    ----------
    functional : callable
        ``functional(domain, *derivatives)`` to be minimized. A callable returning
        either a scalar or an iterable of components which combined using the
        ``combinator`` argument give the value of the functional. A callable
        taking no arguments is also accepted.

    domain : numpy.array or tf.Tensor or tf.Variable
        N dimensional input values as a column vector. ``x.shape = (M,N)`` where
        M is number of examples and N is number of dimensions.
        Hence a one dimensional vector with 100 examples should look like
        ``x.shape = (100, 1)``.

    order : int, optional
        Maximum order of the derivatives appearing in the functional.

    combinator : callable, optional
        A method to combine equations, boundaries and constraints, the identity
        by default.

    batch : bool, default=True
        If False, ``functional`` receives a point in the domain and the values of the
        functions and derivatives at this point. Otherwise, it receives "batches"
        consisting of all the points in the domain and the values of functions and
        derivatives at those points.

    model : dennsolver.nn or tf.keras.Model or tf.keras.Sequential
        A trainable tensorflow model, to represent the solution of the problem

    dtype : tf.dtypes.DType, optional
        dtype of the domain and input layer

    optimizer : str or tensorflow optimizer, optional
        Defining the optimizer to be used, adam by default

    callbacks : list, optional
        These are methods which can interfere with the algorithm where it
        can include LRschedulers or loss monitoring. They take a ``Minimizer`` object
        and return a ``bool``, which is true if the run is to be terminated early.

    metrics : list, optional
        These are the tools to monitor the parameters during the fitting.
        They receive a ``Minimizer`` object and return a dictionary with the names of
        the metrics as keys and their values. These values will be logged.

    epochs : int, optional
        If provided, the model is trained for the specified number of epochs

    verbose: bool, default=False
        If ``epochs`` is provided, whether to print metrics and epoch information while
        training

    **optimizer_params
        Any optimizer-related input depending on the optimizer choosen by the
        user i.e. lr, decay, beta_1, beta_2, etc.

    Returns
    ------
    elvet.Minimizer
    """

    normalizer = _MinimizerInputNormalizer(
        functional=functional,
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

    minimizer_obj = Minimizer(
        functional=normalizer.functional,
        domain=normalizer.domain,
        order=normalizer.order,
        combinator=normalizer.combinator,
        model=normalizer.model,
        optimizer=normalizer.optimizer,
        callbacks=normalizer.callbacks,
        metrics=normalizer.metrics,
    )

    if epochs is not None:
        minimizer_obj.fit(epochs, verbose=verbose)

    return minimizer_obj


class Minimizer:
    """
    Functional minimization problem solver.

    ``Minimizer`` objects are to be constructed using the ``minimizer`` function.

    Attributes
    ----------
    functional : callable
        ``functional(domain, *derivatives)`` to be minimized. A callable returning
        either a scalar or an iterable of components which combined using the
        ``combinator`` attribute give the value of the functional.

    domain : tf.Tensor
        N dimensional input values as a column vector. ``x.shape = (M,N)`` where
        M is number of examples and N is number of dimensions.
        Hence a one dimensional vector with 100 examples should look like
        ``x.shape = (100, 1)``.

    order : int, optional
        Maximum order of the derivatives appearing in the functional. If
        provided, the boundary condition checks will be overwritten.

    combinator : callable
        A method to combine the output of ``functional`` into a scalar.

    model : dennsolver.nn or tf.keras.Model or tf.keras.Sequential
        A trainable tensorflow model representing the solution to the problem

    optimizer : tensorflow optimizer
        optimizer to be used in training the model

    callbacks : list
        These are methods which can interfere with the algorithm where it
        can include LRschedulers or loss monitoring. They take a ``Minimizer`` object
        and return a ``bool``, which is true if the run is to be terminated early.

    metrics : list
        These are the tools to monitor the parameters during the fitting.
        They receive a ``Minimizer`` object and return a dictionary with the names of
        the metrics as keys and their values. These values will be logged.

    losses : list
        History of values of the combined functional over the training procedure.
    """

    def __init__(
        self,
        functional,
        domain,
        order,
        combinator,
        model,
        optimizer,
        callbacks,
        metrics,
    ):
        self.functional = functional
        self._domain = domain
        self.order = order
        self.combinator = combinator
        self.model = model
        self.callbacks = callbacks
        self.metrics = metrics
        self.optimizer = optimizer
        self.losses = []  # for multi-fit runs, store all losses

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, new_domain):
        self._domain = _MinimizerInputNormalizer(
            domain=new_domain,
            dtype=self._domain.dtype,
            model=self.model,
        ).domain

    def prediction(self, numpy=True):
        """
        Calculate the current prediction of the model, a tensro representing the values
        of the current solution at the points in the domain.

        Parameters
        ----------
        numpy: bool, default=True
            whether to return the predicions in the form of a numpy array or a
            tensorflow Tensor.

        Returns
        -------
        numpy or tf.Tensor
        """
        if numpy:
            return self.model(self.domain).numpy()
        else:
            return self.model(self.domain)

    def save_model_weights(self, filepath, overwrite=False):
        if os.path.isfile(filepath) and not overwrite:
            log.error("Weight file already exists.")
            return
        if ".h5" not in filepath:
            filepath = filepath.split(".")[0] + ".h5"
        if hasattr(self.model, "save_weights"):
            self.model.save_weights(filepath)
            log.info("Model saved in " + filepath)

    def load_model_weights(self, filepath, model=None):
        if ".h5" not in filepath:
            filepath = filepath.split(".")[0] + ".h5"
        if not os.path.isfile(filepath):
            log.error("Weight file does not exist.")
            return
        try:
            if model is None:
                self.model.load_weights(filepath)
            else:
                self.model = model.load_weights(filepath)
        except Exception:
            log.error("Can't load the weights. Please check the model.")
            return

    def derivatives(self, domain=None):
        if domain is None:
            domain = self.domain

        derivatives = derivative_stack(
            function=self.model,
            domain=domain,
            max_order=self.order,
            training=True,
        )

        return derivatives

    @tf.function
    def fit_step(self, domain):
        """
        Calculate the combined loss and perform one optimization step.
        """
        with tf.GradientTape() as tape:
            components = self.functional(domain, *self.derivatives(domain))
            loss = self.combinator(components)

        gradients = tape.gradient(loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))

        return components, loss

    def fit(self, epochs, verbose=False, verbose_freq=10000, domain=None):
        """
        Train ``self.model`` to solve the minimization problem.

        Parameters
        ----------
        epochs : int
            number of epochs to run

        verbose: bool, default=False
            whether to print metrics and epoch information

        verbose_freq : int, default=10000
            frequency with which the information will be printed on the screen

        domain : tf.Tensor, optional
            to update ``self.domain``
        """

        start_time = time.time()
        stop = False
        epochs = int(epochs)

        if domain is not None:
            self.domain = domain

        for epoch in range(1, epochs + 1):
            try:
                self.loss_components, self.loss = self.fit_step(self.domain)

            except (ValueError, UnboundLocalError, TypeError) as err:
                log.error("Please check the input parameters.")
                log.error(str(err))
                break

            except KeyboardInterrupt:
                log.warning("Training stopped by the user.")
                stop = True

            self.epoch = epoch
            loss = (
                self.loss.numpy()
                if self.loss.numpy().shape == ()
                else self.loss.numpy()[0]
            )
            self.losses.append(loss)

            for callback in self.callbacks:
                if callback(self):
                    log.warning("Early stop by the user!")
                    stop = True

            print_now = verbose and (
                stop or epoch % verbose_freq == 0 or epoch in (1, epochs)
            )
            if print_now:
                self.metric_results = self._default_metric()

                for metric in self.metrics:
                    try:
                        self.metric_results.update(metric(self))
                    except TypeError as err:
                        raise InvalidMetric(f"Invalid metric! {err}")

                self.print_metric_results(time.time() - start_time)

            if stop:
                break

    def print_metric_results(self, elapsed_time=None):
        epoch_str = f"epoch = {self.metric_results['epoch']}"

        time_str = (
            ""
            if elapsed_time is None
            else (
                "elapsed time = "
                f"{time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}"
            )
        )

        def tensor_str(name, tensor):
            try:
                if np.shape(tensor) != ():
                    strs = (f"{value:.1e}" for value in tensor)
                    return f"{name} = [{', '.join(strs)}]"
                else:
                    return f"{name} = {tensor:.2e}"
            except TypeError as err:
                raise InvalidMetric(
                    "Invalid Metric! Metric needs to return"
                    " a dictionary type {<name> : <value>, }\n" + str(err)
                )

        tensors_str = ", ".join(
            tensor_str(name, tensor)
            for name, tensor in self.metric_results.items()
            if name not in ("epoch", "optimizer")
        )

        log.info(f"{epoch_str}, {tensors_str}, {time_str}")

    def _default_metric(self):
        return {
            "epoch": self.epoch,
            "loss": self.losses[-1],
        }
