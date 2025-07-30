import unittest

import numpy as np
import tensorflow as tf

from elvet import box


class TestBox(unittest.TestCase):
    def setUp(self):
        self.cases = {
            ((0, 1, 1),): [[0]],
            ((3, 4, 2),): [[3], [4]],
            ((-5, -2, 7),): [[-5], [-4.5], [-4], [-3.5], [-3], [-2.5], [-2]],
            ((0, 1, 3), (4, 7, 2)): [
                [0, 4],
                [0.5, 4],
                [1, 4],
                [0, 7],
                [0.5, 7],
                [1, 7],
            ],
        }

    def test_box(self):
        for args, expected in self.cases.items():
            result = box(*args)
            assert (result.numpy() == np.array(expected)).all()
            assert isinstance(result, tf.Tensor)
            assert result.dtype == tf.dtypes.float32


if __name__ == "__main__":
    unittest.main()
