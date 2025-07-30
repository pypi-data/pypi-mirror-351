import unittest

import tensorflow as tf

import elvet


class TestMinimizer(unittest.TestCase):
    def test_minimizer(self):
        distance = 3
        heights = 1, 0
        length = 5

        def loss(x, y, dy):
            dy = dy[:, 0]
            energy = tf.reduce_mean(y * (1 + dy ** 2) ** 0.5) * distance
            current_length = tf.reduce_mean((1 + dy ** 2) ** 0.5) * distance
            bcs = (y[0] - heights[0], y[-1] - heights[1])
            return (
                energy
                + 1e3 * (current_length - length) ** 2
                + 1e2 * sum(bc ** 2 for bc in bcs)
            )

        domain = elvet.box((0, distance, 100))

        minimizer = elvet.minimizer(
            functional=loss,
            domain=domain,
            batch=True,
            model=elvet.nn(1, 10, 1),
            lr=1e-3,
        )
        minimizer.fit(50000, verbose=True)

        assert -3 < minimizer.losses[-1] < -2.5


if __name__ == "__main__":
    unittest.main()
