import tensorflow as tf

from elvet.system.exceptions import InvalidInput
from elvet.utils.unstack import unstack
from elvet.math.diffops.metric_ops import _compute_metric


def laplace_beltrami(
    second_derivatives, y_index=None, metric="euclidean", c=1.0, time_domain=None
):
    """
    Laplace–Beltrami operator
    https://en.wikipedia.org/wiki/Laplace–Beltrami_operator

    .. math::
        \\Delta \\dot y = \\sum_{i,j} g^{ij} \\frac{d^2y_k}{dx^idx^j}

    Parameters
    ----------
    second_derivatives : tf.Tensor
        Second order derivatives.

    y_index : int, optional
        Take the certain dimension of the y-axis If None all will be returned.
        The default is None.

    metric : str or tf.Tensor, optional
        Metric of the problem. The default is 'euclidean'.

    c : float, optional
        Scale of the time domain. The default is 1.

    time_domain : int, optional
        Position of the time domain. If None all axes will be treated as space-like.
        The default is None.

    Raises
    ------
    InvalidInput
        will be raised if second derivative shape is not 3 (non batch mode)
        or 4 (batch mode).

    Returns
    -------
    tf.Tensor
    """
    if len(second_derivatives.shape) == 3:
        x_axes = 0, 1
    elif len(second_derivatives.shape) == 4:
        x_axes = 1, 2
    else:
        raise InvalidInput(
            "len(second_derivatives.shape) =="
            f"{len(second_derivatives.shape)} not in (3, 4)"
        )

    metric = _compute_metric(
        metric, second_derivatives.shape[x_axes[0]], c=c, time_domain=time_domain
    )

    if y_index is None:
        return tf.tensordot(metric, second_derivatives, axes=[[0, 1], list(x_axes)])

    return unstack(
        tf.tensordot(metric, second_derivatives, axes=[[0, 1], list(x_axes)])
    )[y_index]


def laplacian(second_derivatives, y_index=None):
    """
    Compute the Laplacian from a tensor containing all the second derivatives
    https://en.wikipedia.org/wiki/Laplace_operator

    .. math::
        \\Delta \\dot y = \\sum_{i,j} \\delta^{i,j} \\frac{d^2y_k}{dx_idx_j}

    Parameters
    ----------
    second_derivatives : tf.Tensor
        containing all the second derivatives, should have shape either
        ``(size, dim_y, dim_x, dim_x)``, in batch mode, or
        ``(dim_y, dim_x, dim_x)`` in non-batch mode.

    y_index : int, optional
        Take the certain dimension of the y-axis If None all will be returned.
        The default is None.

    Returns
    -------
    tf.Tensor
        Calculated Laplacian.

    """

    return laplace_beltrami(
        second_derivatives, y_index=y_index, metric="euclidean", c=1.0, time_domain=None
    )


def dalembertian(second_derivatives, y_index=None, c=1.0, time_domain=None):
    """
    Compute the d'Alembertian from a tensor containing all the second derivatives
    https://en.wikipedia.org/wiki/D%27Alembert_operator

    .. math::
        \\square = \\partial_0^2 / c^2 - \\partial^i \\partial_i

    Parameters
    ----------
    second_derivatives : tf.Tensor
        containing all the second derivatives, should have shape either
        ``(size, dim_y, dim_x, dim_x)``, in batch mode, or
        ``(dim_y, dim_x, dim_x)`` in non-batch mode

    y_index : int, optional
        Take the certain dimension of the y-axis If None all will be returned.
        The default is None.

    c : float, optional
        to multiply by 1/c the ith component of the metric indicated by time domain.
        The default is 1.0.

    time_domain : int, optional
        Position of the time domain. If None all axses will be treated as space-like.
        The default is None.

    Returns
    -------
    tf.Tensor
        Calculated d'Alembertian operator. with (+---) Minkowski metric
    """

    return laplace_beltrami(
        second_derivatives,
        y_index=y_index,
        metric="mostlyminus",
        c=c,
        time_domain=time_domain,
    )
