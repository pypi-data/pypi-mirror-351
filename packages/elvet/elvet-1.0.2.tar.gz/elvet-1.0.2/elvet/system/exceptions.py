Red = "\x1b[31m"
End = "\x1b[0m"


class InvalidBound(Exception):
    """Invalid Boundary Condition Exception"""

    def __init__(self, message="Invalid Boundary Condition!"):
        super(InvalidBound, self).__init__(Red + message + End)


class InvalidEquation(Exception):
    """Invalid Equation Exception"""

    def __init__(self, message="Invalid Equation!"):
        super(InvalidEquation, self).__init__(Red + message + End)


class InvalidHypothesis(Exception):
    """Invalid Hypothesis Exception"""

    def __init__(self, message="Invalid Hypothesis!!!"):
        message += (
            "\n   * If you are using Keras libraries, please make sure"
            + " that you are using it through TensorFlow."
            + "\n   * If you are designing your own layers please make sure"
            + "that the weight of the model are trainable e.g."
            + "\n       `tf.Variable(Weights, trainable=True)`"
            + "\n     or use `get_weights` function in `tf.keras.layers.Layer`"
        )
        super(InvalidHypothesis, self).__init__(Red + message + End)


class InvalidDomain(Exception):
    """Invalid Domain Exception"""

    def __init__(self, message="Invalid Domain!"):
        super(InvalidDomain, self).__init__(Red + message + End)


class InvalidDataType(Exception):
    """Invalid Data Type Exception"""

    def __init__(self, message="Invalid Data Type!"):
        super(InvalidDataType, self).__init__(Red + message + End)


class InvalidLRScheduler(Exception):
    """Invalid Learning Rate scheduler"""

    def __init__(self, message="Invalid Learning Rate scheduler!"):
        super(InvalidLRScheduler, self).__init__(Red + message + End)


class InvalidMetric(Exception):
    """Invalid Metric Exception"""

    def __init__(self, message="Invalid Metric!"):
        super(InvalidMetric, self).__init__(Red + message + End)


class InvalidAlgebraicForm(Exception):
    """Invalid Algebraic Form Exception"""

    def __init__(self, message="Invalid Algebraic Form!"):
        super(InvalidAlgebraicForm, self).__init__(Red + message + End)


class InvalidInput(Exception):
    """Invalid Domain Exception"""

    def __init__(self, message="Invalid Input!"):
        super(InvalidInput, self).__init__(Red + message + End)


class UndefinedMetric(Exception):
    """Undefined Metric Exception"""

    def __init__(self, metric_str):
        super().__init__(f"String metric not defined: {metric_str}")
