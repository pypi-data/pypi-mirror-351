from itertools import product
import unittest

import numpy as np
import tensorflow as tf

from elvet.math.derivative import derivative


class TestDerivativesOneDim(unittest.TestCase):
    def setUp(self):
        self.f = lambda x: x ** 2 + 5 * x - 3 * tf.math.exp(-x / 7) + 8
        self.df = lambda x: 2 * x + 5 + 3 / 7 * tf.math.exp(-x / 7)
        self.d2f = lambda x: 2 - 3 / 7 ** 2 * tf.math.exp(-x / 7)
        self.d3f = lambda x: 3 / 7 ** 3 * tf.math.exp(-x / 7)

        self.x_values = [
            tf.convert_to_tensor([x], dtype=tf.dtypes.float32)
            for x in [1.0, -3.0, 12.9, -37.2, 0.034]
        ]

    def test_first_derivatives(self):
        for x in self.x_values:
            assert np.isclose(derivative(self.f, x, 1), self.df(x))

    def test_second_derivatives(self):
        for x in self.x_values:
            assert np.isclose(derivative(self.f, x, 2), self.d2f(x))

    def test_third_derivatives(self):
        for x in self.x_values:
            assert np.isclose(derivative(self.f, x, 3), self.d3f(x))


class TestDerivativesMultiDim(unittest.TestCase):
    def test_second_derivatives(self):
        def f(x):
            return tf.reshape(
                x[:, 0] ** 2
                + 7 * x[:, 0] * x[:, 1]
                + 11 * x[:, 1] ** 2
                + x[:, 0] ** 3 * x[:, 1] ** 4,
                (x.shape[0], 1),
            )

        def d2f(x):
            return np.array(
                [
                    [
                        (2 + 3 * 2 * x[:, 0] * x[:, 1] ** 4),
                        (7 + 3 * 4 * x[:, 0] ** 2 * x[:, 1] ** 3),
                    ],
                    [
                        (7 + 3 * 4 * x[:, 0] ** 2 * x[:, 1] ** 3),
                        (22 + 4 * 3 * x[:, 0] ** 3 * x[:, 1] ** 2),
                    ],
                ]
            )

        x_values = [
            tf.convert_to_tensor([[x1, x2]], dtype=tf.dtypes.float32)
            for x1, x2 in product([0.0, 1.0, -3.0, 12.9, 0.034], repeat=2)
        ]

        for x in x_values:
            assert np.all(np.isclose(derivative(f, x, 2), d2f(x)))


if __name__ == "__main__":
    unittest.main()
