import tensorflow as tf
from inspect import getfullargspec

from elvet.system.exceptions import InvalidInput


# to make tf less vocal
tf.get_logger().setLevel("ERROR")


def derivative_stack(function, domain, max_order, training=False):
    """
    Compute a list of derivatives of ``function``.

    The nth element in the list is a tensor representing the derivative of order ``n``:

    .. math::
        {\\rm stack[n][i, j, \\ldots, k]}
        = \\partial_i \\partial_j \\ldots y_k
        = \\frac{\\partial^n}{\\partial x_i \\partial x_j  \\ldots} y_k

    Parameters
    ----------
    function : callable
        To be differentiated, taking an input of shape ``(size, dim_x)`` or ``(dim_x,)``
        and having an output of shape ``(size, dim_y)`` or ``(dim_y,)``, respectively.

    domain : tf.Tensor
        Of shape ``(size, dim_x)`` or ``(dim_x,)``, set of points with respect to and
        at which the function is to be differentiated.

    max_order : int
        Maximum order of the derivatives to be computed.

    Returns
    -------
    stack : list
        with ``stack[order]`` being a ``tf.Tensor`` with shape:
        ``(size,) + (dim_x,)*order + (dim_y,)`` or ``(dim_x,)*order + (dim_y,)``
    """

    batch = _is_batched(domain)
    if not batch:
        function, domain = _make_batch(function, domain)

    size = domain.shape[0]
    dim_x = domain.shape[1]

    stack = []

    # TODO: @JACK find a way to avoid persistent execution
    with tf.GradientTape(persistent=True) as diff_tape:
        diff_tape.watch(domain)

        if "training" in getfullargspec(function).args:
            derivatives = function(domain, training=training)
        else:
            derivatives = function(domain)

        stack.append(derivatives)

        dim_y = derivatives.shape[-1]

        for order in range(1, max_order + 1):
            shape = (size, dim_x ** (order - 1) * dim_y)
            components = tf.unstack(tf.reshape(derivatives, shape), axis=1)

            derivatives = tf.stack(
                [diff_tape.gradient(component, domain) for component in components],
                axis=2,
            )

            stack_shape = (size,) + (dim_x,) * order + (dim_y,)

            if not batch:
                stack_shape = stack_shape[1:]

            stack.append(tf.reshape(derivatives, stack_shape))

    return stack


def derivative(function, domain, order, training=False):
    """
    Compute the ``order`` th ``derivatives`` of ``function``.

    .. math::
        {\\rm derivatives[i, j, \\ldots, k]}
        = \\partial_i \\partial_j \\ldots y_k
        = \\frac{\\partial^n}{\\partial x_i \\partial x_j  \\ldots} y_k

    Parameters
    ----------
    function : callable
        To be differentiated, taking an input of shape ``(size, dim_x)`` or ``(dim_x,)``
        and having an output of shape ``(size, dim_y)`` or ``(dim_y,)``, respectively.

    domain : tf.Tensor
        Of shape ``(size, dim_x)`` or ``(dim_x,)``, set of points with respect to and
        at which the function is to be differentiated.

    order : int
        Order of the derivatives to be computed.

    Returns
    -------
    derivatives : ``tf.Tensor``
        Of shape: ``(size,) + (dim_x,)*order + (dim_y,)`` or
        ``(dim_x,)*order + (dim_y,)``.
    """

    return derivative_stack(
        function=function,
        domain=domain,
        max_order=order,
        training=training,
    )[order]


def _is_batched(domain):
    if len(domain.shape) == 1:
        return False
    elif len(domain.shape) == 2:
        return True
    else:
        raise InvalidInput(
            f"len(domain.shape) == " f"{len(domain.shape)} not in (1, 2)"
        )


def _make_batch(function, domain):
    batched_domain = tf.expand_dims(domain, axis=0)

    def batched_function(x):
        x = tf.squeeze(x, axis=0)
        function_value = function(x)

        if function_value.shape == ():
            return tf.reshape(function_value, (1, 1))
        else:
            return tf.expand_dims(function_value, axis=0)

    return batched_function, batched_domain
