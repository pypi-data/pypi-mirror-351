import unittest

import numpy as np
import tensorflow as tf

from elvet import box
from elvet.math import integral, integration_methods


class TestIntegral(unittest.TestCase):
    def test_integral(self):
        x = box((0, np.pi, 10))

        for method in integration_methods:
            assert np.isclose(
                integral(tf.sin, x, method=method).numpy()[0],
                2,
                rtol=0.8,
            )


if __name__ == "__main__":
    unittest.main()
