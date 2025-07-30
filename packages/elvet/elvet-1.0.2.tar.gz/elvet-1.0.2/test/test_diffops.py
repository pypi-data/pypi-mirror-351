import unittest

import tensorflow as tf
import numpy as np

from elvet.math.derivative import derivative
from elvet.math import divergence, curl, laplacian


class TestDiffOps(unittest.TestCase):
    def setUp(self):
        # Define the electric potential of a sphere filled with uniform charge. Elvet's
        # derivative is just the gradient: the electric field. The curl of the electric
        # field should vanish. Its divergence should be equal to the Laplacian of the
        # potential, and should be equal to the charge density.

        self.inside = tf.convert_to_tensor([0.1, 0.7, 0.4], dtype=tf.float32)
        self.outside = tf.convert_to_tensor([1.1, 1.7, 1.4], dtype=tf.float32)

        def V(x):
            r = (x[0] ** 2 + x[1] ** 2 + x[2] ** 2) ** 0.5
            if r < 1:
                return (3 - r ** 2) / 2
            else:
                return 1 / r

        self.V = V
        self.d2V = lambda x: derivative(V, x, order=2)
        self.E = lambda x: tf.squeeze(derivative(V, x, order=1), axis=-1)
        self.dE = lambda x: derivative(self.E, x, order=1)

    def test_curl(self):
        assert np.isclose(curl(self.dE(self.inside)), 0).all()
        assert np.isclose(curl(self.dE(self.outside)), 0).all()

    def test_divergence(self):
        assert np.isclose(divergence(self.dE(self.inside)), -3).all()
        assert np.isclose(divergence(self.dE(self.outside)), 0).all()

    def test_laplacian(self):
        assert np.isclose(laplacian(self.d2V(self.inside)), -3).all()
        assert np.isclose(laplacian(self.d2V(self.outside)), 0).all()


if __name__ == "__main__":
    unittest.main()
