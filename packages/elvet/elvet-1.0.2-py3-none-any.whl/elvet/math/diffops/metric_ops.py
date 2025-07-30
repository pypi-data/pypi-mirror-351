import tensorflow as tf

from elvet.system.exceptions import UndefinedMetric

metrics = ["euclidean", "mostlyplus", "mostlyminus"]
"""
String representation of the most common metrics to be passed to ``divergence`` and
 ``laplacian``:

* `'euclidean'` is the Euclidean metric

* `'mostlyplus'` is the Lorentzian metric in the mostly-plus convention

* `'mostlyminus'` is the Lorentzian metric in the mostly-minus convention

The Lorentzian versions also adopt the convention that time is the first coordinate.
"""


def _compute_metric(metric, dimension, c=1.0, time_domain=None):
    """
    Parameters
    ----------
    metric : str or tf.Tensor
        The definition of the metric
    dimension : int
        dimensions of the derivative
    c : float, optional
        Scaling constant for time domain. The default is 1..
    time_domain : int, optional
        Position of the time domain. If None all axses will be treated as space-like.
        The default is None.

    Raises
    ------
    UndefinedMetric
        Will be raised if metric is not str or tf.Tensor.

    Returns
    -------
    tf.Tensor
        Diagonal tensor.

    """
    if not isinstance(metric, str):
        return metric

    normalized_metric = metric.replace("_", "").lower()

    if normalized_metric == "euclidean":
        space_sign, time_sign = 1.0, 1.0
    elif normalized_metric == "mostlyplus":
        space_sign, time_sign = 1.0, -1.0
    elif normalized_metric == "mostlyminus":
        space_sign, time_sign = -1.0, 1.0
    else:
        raise UndefinedMetric(str(metric))

    diag = [
        space_sign if x != time_domain else time_sign / c ** 2 for x in range(dimension)
    ]
    return tf.linalg.diag(diag)
