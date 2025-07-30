import tensorflow as tf


def nn(*sizes, activation=tf.nn.sigmoid, dtype=tf.float32):
    """
    Construct a fully connected neural network. Example::

       net = nn(1, 10, 1)

    Parameters
    ----------
    *sizes
        Number of units in the input layer, hidden layers and output layer.

    activation: callable, default=tf.nn.sigmoid
        Activation function, for hidden layers only.

    dtype: tf.dtypes.DType, default=tf.float32
        Data type of the network.
    """

    return tf.keras.Sequential(
        [tf.keras.Input(shape=(sizes[0],), dtype=dtype)]
        + [
            tf.keras.layers.Dense(size, activation=activation, dtype=dtype)
            for size in sizes[1:-1]
        ]
        + [tf.keras.layers.Dense(sizes[-1], activation=None, dtype=dtype)]
    )
