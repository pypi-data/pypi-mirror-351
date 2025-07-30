from collections.abc import Iterable
import logging

import numpy as np
import tensorflow as tf

log = logging.getLogger("Elvet")


def box(*limits, endpoint=True, dtype=tf.float32):
    """
    Generate a grid of equally-spaced points in a "box": a product of intervals.

    For example, a rectangle between the points (2, 3) and (5, 8) containing 200
    points is generated through::

        elvet.box((2, 5, 10), (3, 8, 20))

    Parameters
    ----------
    *limits
        Each limit should be a tuple ``(lower, upper, n_points)`` with ``lower`` and
        ``upper`` being floats and ``n_points`` being an int.

    endpoint: bool, default=True
        Whether to include the upper value of each interval.

    dtype: tf.dtypes.DType, default=tf.float32
        dtype of the output

    Returns
    -------
    grid : tf.Tensor
        Of shape ``(n_product_points, len(limits))`` where ``n_product_points is the
        product of all the ``n_points`` of each limit. Each ``grid[i]`` represents
        a point in the grid. The grid is defined as the product of subgrids defined by
        each ``limit`` tuple. The subgrid corresponding to ``(lower, upper, n_points)``
        is the set of ``n_points`` equally-spaced floats between ``lower`` and
        ``upper``.
    """
    if all([len(limit) == 3 for limit in limits]):
        axes = (
            np.linspace(lower, upper, n_points, endpoint=endpoint)
            for lower, upper, n_points in limits
        )

        array = np.vstack([coordinate.flatten() for coordinate in np.meshgrid(*axes)]).T

        return tf.constant(array, dtype=dtype)

    else:
        log.error(
            "Invalid syntax! Each limit requires 3 inputs: (lower, upper, n_points)"
        )
        return


def cut_domain(domain, conditions, dtype=None):
    """
    Take a domain, which is a set of points, and return the subset of points that
    satisfy all the given conditions.

    Parameters
    ----------
    domain : tf.Tensor
        of shape ``(batch_size, dim_x)``, to be cut.

    conditions : callable
        Taking a point in domain as argument and returning a bool or a list of bools.

    dtype : tf.dtypes.DType
        dtype of the output.

    Returns
    -------
    cut : tf.Tensor
        of shape ``(new_batch_size, dim_x)``, with the elements ``cut[i]`` representing
        the points ``domain[j]`` in the original domain such that all
        ``conditions(domain[j])`` are satisfied.
    """

    # Convert output of conditions into a list
    if not isinstance(conditions(domain[0]), Iterable):

        def _conditions(point):
            return [conditions(point)]

        conditions = _conditions

    # Convert domain to numpy and obtain dtype
    if not isinstance(domain, np.ndarray):
        domain = domain.numpy()
        if dtype is None:
            dtype = tf.dtypes.float32
    elif dtype is None:
        dtype = domain.dtype

    # Obtain new points
    size, dim = domain.shape
    points = [domain[i] for i in range(size) if np.all(conditions(domain[i]))]

    return tf.convert_to_tensor(points, dtype=dtype)


def ellipsoid(center, semiaxes, n_points):
    """
    Generate a "box" domain and cut it to form an ellipsoid.

    Parameters
    ----------
    center : tuple
        Coordinates of the center.

    semiaxes : tuple
        Sizes of the semiaxes, must satisfy ``len(semiaxes) == len(center)``.

    n_points : int
        Number of points to be found inside the ellipsoid.

    Returns
    -------
    tf.Tensor
        Of shape ``(batch_size, len(center))``, with ``batch_size`` being as close
        to ``n_points`` as possible.
    """

    n_points_axis = int(
        np.ceil(2 * (n_points / (4 / 3 * np.pi)) ** (1 / len(semiaxes)))
    )

    mins = (c - s for c, s in zip(center, semiaxes))
    maxs = (c + s for c, s in zip(center, semiaxes))

    domain = box(*((min_, max_, n_points_axis) for min_, max_ in zip(mins, maxs)))

    def conditions(point):
        return sum(((x - c) / s) ** 2 for s, x, c in zip(semiaxes, point, center)) < 1

    return cut_domain(domain, conditions)
