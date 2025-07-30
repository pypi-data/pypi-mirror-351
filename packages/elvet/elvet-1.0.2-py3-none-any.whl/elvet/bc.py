import tensorflow as tf

from elvet.utils.unstack import unstack
from elvet.system.exceptions import InvalidBound


class BC:
    """
    Represents a boundary condition, given by an equation

    .. math::
        {\\rm equation}\\left(
            x_i,
            \\frac{\\partial}{\\partial x_i} y_j,
            \\frac{\\partial^2}{\\partial x_i \\partial x_j} y_k,
            \\ldots
        \\right) = 0

    that must be satisfied at set of points :math:`x` such that :math:`x_{i_1} = p_1`,
    :math:`x_{i_2} = p_2`, :math:`\\ldots`.

    For example, the condition :math:`y(0) = 1` for a first order differential equation
    would be given as::

        bc = BC(0, lambda x, y, dy: y - 1)

    Parameters
    ----------
    point : float or tuple of floats
        Values of the fixed coordinates :math:`x_{i_k} = p_k`

    equation : callable
        Function ``equation(x, y, dy, ...)`` giving the condition to be satisfied.

    index : int or tuple of ints
        Indices :math:`i_k` of the fixed coordinates :math:`x_{i_k} = p_k`.
    """

    def __init__(self, point, equation, index=0):
        self.point = point
        self.equation = equation
        self.index = index

        # if either one of the point or index inputs are list or tuple
        # both needs to be list or tuple.
        if any(isinstance(x, (list, tuple)) for x in [point, index]):
            if not all(isinstance(x, (list, tuple)) for x in [point, index]):
                raise InvalidBound(
                    "Either both point and axes needs to be " "list or numeric type"
                )
            elif len(point) != len(index):
                raise InvalidBound(
                    "Number of boundary values is not equal to "
                    f"the number of axses {len(point)}!={len(index)}"
                )

    def __call__(self, domain, *nth_derivatives):
        # if points and axes are given as a list do a multi conditioning
        if isinstance(self.point, (list, tuple)):
            multicond_list = [
                unstack(domain)[xi] == cond for xi, cond in zip(self.index, self.point)
            ]
            condition = multicond_list[0]

            for icond in multicond_list[1:]:
                condition = tf.math.logical_and(condition, icond)

            return tf.where(condition, self.equation(domain, *nth_derivatives), 0.0)

        return tf.where(
            unstack(domain)[self.index] == self.point,
            self.equation(domain, *nth_derivatives),
            0.0,
        )
