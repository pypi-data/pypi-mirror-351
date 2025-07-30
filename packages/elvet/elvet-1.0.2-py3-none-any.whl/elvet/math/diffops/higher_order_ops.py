from elvet.system.exceptions import InvalidInput
from elvet.utils.unstack import unstack


# TODO @Jack find a way to automatically understand if its batched or not
def diagonals(derivative, y_index=None, return_list=False, batch=True):
    """
    Extract the diagonal elements of a higher dimensional derivative tensor.

    .. math::
        \\sum_{j} \\frac{\\partial^n y_i}{\\partial^n x_j}

    Parameters
    ----------
    derivative : tf.Tensor
        Derivative tensor of arbitrary order.
    y_index : int, optional
        Index of the y-axis. If None, all y components will be returned.
        The default is None.
    return_list : bool, optional
        If True, returns all the diagonal terms of the derivative tensor as a list. If
        False returns sum of the diagonal terms. The default is False.
    batch : bool, optional
        If ``True``, batch mode will be assumed where derivative shape is
        ``(size, (xdim,)*order, ydim)``. If ``False`` non-batched mode will assumed
        where derivative shape is ``((xdim,)*order, ydim)``. The default is True.

    Raises
    ------
    InvalidInput
        Raises if the if the derivative order is less than 1.

    Returns
    -------
    tf.Tensor or list of tf.Tensor

    """

    ydim = derivative.shape[-1]

    if batch:
        xdim = derivative.shape[1]
        order = len(derivative.shape) - 2
        size = derivative.shape[0]
        if len(derivative.shape) < 3:
            raise InvalidInput("Expected at least first order derivative.")
        indices = [
            tuple([slice(size), *(i,) * order, slice(ydim)]) for i in range(xdim)
        ]
    else:
        xdim = derivative.shape[0]
        order = len(derivative.shape) - 1
        if len(derivative.shape) < 2:
            raise InvalidInput("Expected at least first order derivative.")
        indices = [tuple([*(i,) * order, slice(ydim)]) for i in range(xdim)]
    if y_index is None:

        def get_yindex(x):
            return x

    else:

        def get_yindex(x):
            return unstack(x)[y_index]

    diagonal_terms = [get_yindex(derivative[ind]) for ind in indices]

    if not return_list:
        return sum(diagonal_terms)

    return diagonal_terms
