import unittest

import numpy as np
import tensorflow as tf

from elvet.bc import BC
from elvet.utils.unstack import unstack


class TestBox(unittest.TestCase):
    def setUp(self):
        def boundary_equation(x, y):
            return unstack(x)[0] ** 2 + unstack(x)[1] ** 3 + unstack(x)[2]

        x = np.array(
            [[1, 2, 3, 4, 5, 6, 7], [1, 2, 3, 4, 5, 6, 7], [1, 2, 3, 4, 5, 6, 7]],
            dtype=float,
        )
        x = x.reshape((7, 3))

        self.x = tf.constant(x, dtype=tf.float32)
        self.bc1 = BC(1, boundary_equation, 0)
        self.bc2 = BC([1, 2, 3], boundary_equation, [0, 1, 2])

    def test_box(self):
        assert (
            (
                self.bc1(self.x, self.x)
                == tf.reshape(
                    tf.constant(np.array([12, 0, 0, 0, 0, 0, 0]), dtype=tf.float32),
                    (7, 1),
                )
            )
            .numpy()
            .all()
        )

        assert (
            (
                self.bc2(self.x, self.x)
                == tf.reshape(
                    tf.constant(np.array([12, 0, 0, 0, 0, 0, 0]), dtype=tf.float32),
                    (7, 1),
                )
            )
            .numpy()
            .all()
        )


if __name__ == "__main__":
    unittest.main()
