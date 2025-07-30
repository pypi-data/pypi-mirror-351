import tensorflow as tf


def delta(domain):
    return (domain[-1] - domain[0]) / (domain.shape[0] - 1)


def left_riemann(function_values, domain):
    return tf.reduce_sum(function_values[:-1]) * delta(domain)


def right_riemann(function_values, domain):
    return tf.reduce_sum(function_values[1:]) * delta(domain)


def trapezoidal(function_values, domain):
    return delta(domain) * (
        (function_values[0] + function_values[-1]) / 2
        + tf.reduce_sum(function_values[1:-1])
    )


def simpson(function_values, domain):
    return (
        delta(domain)
        / 3
        * (
            function_values[0]
            + function_values[-1]
            + 4 * tf.reduce_sum(function_values[1:-1:2])
            + 2 * tf.reduce_sum(function_values[2:-1:2])
        )
    )


def boole(function_values, domain):
    return (
        delta(domain)
        / 45
        * (
            14 * (function_values[0] + function_values[-1])
            + 64 * tf.reduce_sum(function_values[1:-1:2])
            + 24 * tf.reduce_sum(function_values[2:-1:4])
            + 28 * tf.reduce_sum(function_values[4:-1:4])
        )
    )


def romberg(function_values, domain):
    n_intervals = domain.shape[0] - 1
    k = (n_intervals - 1).bit_length()
    h = domain[-1] - domain[0]

    R = {(0, 0): (function_values[0] + function_values[-1]) / (2 * h)}

    start = stop = step = n_intervals

    for i in range(1, k + 1):
        start >>= 1
        R[(i, 0)] = (
            R[(i - 1, 0)] + h * tf.reduce_sum(function_values[start:stop:step])
        ) / 2
        step >>= 1

        for j in range(1, i + 1):
            previous = R[(i, j - 1)]
            R[(i, j)] = previous + (previous - R[(i - 1, j - 1)]) / ((1 << (2 * j)) - 1)

        h /= 2

    return R[(k, k)]


_integration_functions = {
    "leftriemann": left_riemann,
    "rightriemann": right_riemann,
    "trapezoidal": trapezoidal,
    "simpson": simpson,
    "boole": boole,
    "romberg": romberg,
}

integration_methods = list(_integration_functions.keys())
"""
Allowed integration methods to be passed to ``integral``
"""


def integral(function_values, domain, method="trapezoidal"):
    """
    Compute the integral of a function over a given domain

    Parameters
    ----------
    function_values : tf.Tensor or callable
        values of the function at the points in the domain, or the function itself

    domain : tf.Tensor
        points in the domain at which the function is evaluated to compute the integral

    integration_method : str, default='trapezoidal'
        represents the integration method, to be chosen from the list
        ``integration_methods``
    """

    if hasattr(function_values, "__call__"):
        function_values = function_values(domain)

    method = method.replace("_", "").lower()

    return _integration_functions[method](function_values, domain)
