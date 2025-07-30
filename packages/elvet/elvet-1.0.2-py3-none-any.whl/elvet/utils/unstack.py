import tensorflow as tf


def unstack(multidim_input: tf.Tensor, axis=None) -> list:
    """
    Modified version of tensorflow's unstack. Behaves exactly in the same way
    except when the shape of the input tensor is of the form ``(size, dim)``,
    and ``axis`` is provided, in which case, instead of returning a list of
    tensors with shape ``(size,)`` or ``(dim,)``, it returns a list of tensors
    with shape ``(size, 1)`` or ``(dim, 1)``.

    For example::

        x = np.array([[1, 2], [3, 4]])
        f = lambda x : tf.pow(x, 3)
        d2y = derivative(f, x, 2)

        unstack(dx2)[0]  # -> x1 dimension
        unstack(dx2)[1]  # -> x2 dimension

    Parameters
    ----------
    multidim_input : tf.Tensor
        To be unstacked.

    axis : int, optional
        Along which to unstack.

    Returns
    -------
    list of tf.Tensor
    """
    if axis is not None:
        return tf.unstack(multidim_input, axis=axis)

    elif len(multidim_input.shape) == 2:
        return [
            tf.reshape(x, (x.shape[0], 1)) for x in tf.unstack(multidim_input, axis=1)
        ]

    return tf.unstack(multidim_input)
