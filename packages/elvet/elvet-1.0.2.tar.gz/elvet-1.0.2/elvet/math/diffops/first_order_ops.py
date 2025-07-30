import tensorflow as tf

from elvet.system.exceptions import InvalidInput
from elvet.math.diffops.metric_ops import _compute_metric


def manifold_divergence(first_derivatives, metric="euclidean", c=1.0, time_domain=None):
    """
    Compute divergence over a specific manifold.

    .. math::
        \\nabla \\dot y = \\sum_{j} g^{ij} \\frac{dy_i}{dx^j}

    Parameters
    ----------
    first_derivatives : tf.Tensor
        First derivative of the function.

    metric : str, optional
        Metric of the manifold. The default is "euclidean".

    c : float, optional
        Scaling constant of the time domain. The default is 1.0.

    time_domain : int, optional
        Position of the time domain. If None all axses will be treated as space-like.
        The default is None.

    Raises
    ------
    InvalidInput
        Will be raised if first derivative shape length is not 2 (non batch mode)
        or not 3 (batch mode).

    Returns
    -------
    tf.Tensor
    """
    if len(first_derivatives.shape) == 2:
        y_axis, x_axis = 1, 0
    elif len(first_derivatives.shape) == 3:
        y_axis, x_axis = 2, 1
    else:
        raise InvalidInput(
            f"len(first_derivatives.shape) == "
            f"{len(first_derivatives.shape)} not in (2, 3)"
        )

    if first_derivatives.shape[y_axis] != first_derivatives.shape[x_axis]:
        raise InvalidInput(
            f"dimY = {first_derivatives.shape[y_axis]} != "
            f"dimX = {first_derivatives.shape[x_axis]} "
        )

    metric = _compute_metric(
        metric, first_derivatives.shape[y_axis], c=c, time_domain=time_domain
    )

    return tf.tensordot(metric, first_derivatives, axes=[[0, 1], [y_axis, x_axis]])


def divergence(first_derivatives):
    """
    Compute the divergence from a tensor containing all the first derivatives
    https://en.wikipedia.org/wiki/Divergence

    .. math::
        \\nabla \\dot y = \\sum_{j} \\frac{dy_i}{dx_j}

    Parameters
    ----------
    first_derivatives : tf.Tensor
        containing all the first derivatives, should have shape either
        ``(size, dim_y, dim_x)``, in batch mode, or ``(dim_y, dim_x)`` in non-batch mode

    Returns
    -------
    tf.Tensor
    """

    return manifold_divergence(first_derivatives)


def curl(first_derivatives):
    """
    Compute the curl from a tensor containing all the first derivatives
    https://en.wikipedia.org/wiki/Curl_(mathematics)

    .. math::
        \\nabla \\times y = \\left(
            \\frac{dy_3}{dx_2} - \\frac{dy_2}{dx_3},
            \\frac{dy_1}{dx_3} - \\frac{dy_3}{dx_1},
            \\frac{dy_2}{dx_1} - \\frac{dy_1}{dx_2}
        \\right)

    Parameters
    ----------
    first_derivatives : tf.Tensor
        containing all the first derivatives, should have shape either
        ``(size, 3, 3)``, in batch mode, or ``(3, 3)`` in non-batch mode

    Returns
    -------
    tf.Tensor
    """
    if len(first_derivatives.shape) == 2:
        x_axis, y_axis = 0, 1
    elif len(first_derivatives.shape) == 3:
        x_axis, y_axis = 1, 2
    else:
        raise InvalidInput(
            f"first_derivatives.shape == {first_derivatives.shape} not in (2, 3)"
        )

    if first_derivatives.shape[y_axis] != 3 or first_derivatives.shape[x_axis] != 3:
        raise InvalidInput(
            "Tree dimensional y and x required, but "
            + f"ydim = {first_derivatives.shape[y_axis]}, "
            + f"xdim = {first_derivatives.shape[x_axis]} received."
        )

    dy1, dy2, dy3 = tf.unstack(first_derivatives, axis=y_axis)

    _, dy1_dx2, dy1_dx3 = tf.unstack(dy1, axis=x_axis)
    dy2_dx1, _, dy2_dx3 = tf.unstack(dy2, axis=x_axis)
    dy3_dx1, dy3_dx2, _ = tf.unstack(dy3, axis=x_axis)

    return tf.stack(
        [dy3_dx2 - dy2_dx3, dy1_dx3 - dy3_dx1, dy2_dx1 - dy1_dx2],
        axis=0,
    )
