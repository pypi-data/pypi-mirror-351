from elvet.models import nn
from elvet.solver.solver import solver


def fitter(
    domain,
    values,
    model=None,
    epochs=None,
    verbose=True,
    **kwargs,
):
    """
    Frontend for fitting a model to reproduce a function :math:`y(x)` from a set of
    points :math:`(x_i, y_i)`. This fitting problem can be viewed as solving the
    "order-0 differential equation":

    .. math::

        y(x_i) - y_i = 0,  \\forall i

    Parameters
    ----------
    domain : tf.Tensor
        of shape ``(batch_size, dim_x)`` with ``domain[i]`` being the point :math:`x_i`
        in the domain

    values : tf.Tensor
        of shape ``(batch_size, dim_y)`` with ``values[i]`` being the value
        :math:`y_i` of the function :math:`y` to be reproduced, at the point
        :math:`x_i`.

    model : dennsolver.nn or tf.keras.Model or tf.keras.Sequential
        A trainable tensorflow model, to represent the function :math:`y`.

    epochs : int, optional
        if provided, the model is trained for the specified number of epochs

    verbose: bool, default=False
        If ``epochs`` is provided, whether to print metrics and epoch information while
        training.

    Returns
    -------
    elvet.Solver
    """

    if model is None:
        model = nn(1, 10, 1)

    result = solver(
        equations=(lambda x, y: y - values),
        bcs=[],
        domain=domain,
        batch=True,
        model=model,
        **kwargs,
    )

    if isinstance(epochs, (int, float)):
        result.fit(int(epochs), verbose=verbose)

    return result
