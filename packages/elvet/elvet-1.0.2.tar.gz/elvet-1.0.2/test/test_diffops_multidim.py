import unittest

import tensorflow as tf

import elvet
from elvet import unstack


class TestDiffOps(unittest.TestCase):
    def setUp(self):
        """
        Define tree random function and stacked versions of this functions to be able to
        cross check all the functionality of the differential operators. *For Batch Mode*
        """
        self.fx_1 = lambda x: unstack(x)[0] ** 2 + unstack(x)[1] ** 3
        self.fx_2 = lambda x: unstack(x)[0] ** 3 + unstack(x)[1]
        self.fx_3 = lambda x: unstack(x)[0] ** 5 * unstack(x)[1] ** 2

        self.fx_12 = lambda x: tf.reshape(
            tf.stack(
                [
                    unstack(x)[0] ** 2 + unstack(x)[1] ** 3,
                    unstack(x)[0] ** 3 + unstack(x)[1],
                ],
                axis=1,
            ),
            (x.shape[0], 2),
        )

        self.fx_123 = lambda x: tf.reshape(
            tf.stack(
                [
                    unstack(x)[0] ** 2 + unstack(x)[1] ** 3,
                    unstack(x)[0] ** 3 + unstack(x)[1],
                    unstack(x)[0] ** 5 * unstack(x)[1] ** 2,
                ],
                axis=1,
            ),
            (x.shape[0], 3),
        )

        self.x = elvet.constant([[1.0, 2.0], [3.0, 4.0]])

        self.dy_1 = elvet.math.derivative(self.fx_1, self.x, 1)
        self.dy_2 = elvet.math.derivative(self.fx_2, self.x, 1)
        self.dy_3 = elvet.math.derivative(self.fx_3, self.x, 1)
        self.dy_12 = elvet.math.derivative(self.fx_12, self.x, 1)
        self.dy_123 = elvet.math.derivative(self.fx_123, self.x, 1)

        self.d2y_1 = elvet.math.derivative(self.fx_1, self.x, 2)
        self.d2y_2 = elvet.math.derivative(self.fx_2, self.x, 2)
        self.d2y_3 = elvet.math.derivative(self.fx_3, self.x, 2)
        self.d2y_12 = elvet.math.derivative(self.fx_12, self.x, 2)
        self.d2y_123 = elvet.math.derivative(self.fx_123, self.x, 2)

    def test_functions(self):
        tf.assert_equal(self.fx_1(self.x), unstack(self.fx_12(self.x))[0])
        tf.assert_equal(self.fx_2(self.x), unstack(self.fx_12(self.x))[1])
        tf.assert_equal(self.fx_3(self.x), unstack(self.fx_123(self.x))[2])

    def test_first_order_derivatives(self):
        y_index = 0
        tf.assert_equal(self.dy_1[:, 0, :], unstack(self.dy_12[:, 0, :])[y_index])
        tf.assert_equal(
            unstack(self.dy_1[:, 0, :])[0], unstack(self.dy_12[:, 0, :])[y_index]
        )

        tf.assert_equal(self.dy_1[:, 0, :], unstack(self.dy_123[:, 0, :])[y_index])
        tf.assert_equal(
            unstack(self.dy_1[:, 0, :])[0], unstack(self.dy_123[:, 0, :])[y_index]
        )

        tf.assert_equal(self.dy_1[:, 1, :], unstack(self.dy_12[:, 1, :])[y_index])
        tf.assert_equal(
            unstack(self.dy_1[:, 1, :])[0], unstack(self.dy_12[:, 1, :])[y_index]
        )

        tf.assert_equal(self.dy_1[:, 1, :], unstack(self.dy_123[:, 1, :])[y_index])
        tf.assert_equal(
            unstack(self.dy_1[:, 1, :])[0], unstack(self.dy_123[:, 1, :])[y_index]
        )

        tf.assert_equal(self.dy_1[:, 0, :], unstack(self.dy_1[:, 0, :])[0])
        tf.assert_equal(self.dy_1[:, 1, :], unstack(self.dy_1[:, 1, :])[0])

        y_index = 1
        tf.assert_equal(self.dy_2[:, 0, :], unstack(self.dy_12[:, 0, :])[y_index])
        tf.assert_equal(
            unstack(self.dy_2[:, 0, :])[0], unstack(self.dy_12[:, 0, :])[y_index]
        )

        tf.assert_equal(self.dy_2[:, 1, :], unstack(self.dy_12[:, 1, :])[y_index])
        tf.assert_equal(
            unstack(self.dy_2[:, 1, :])[0], unstack(self.dy_12[:, 1, :])[y_index]
        )

        tf.assert_equal(self.dy_2[:, 0, :], unstack(self.dy_123[:, 0, :])[y_index])
        tf.assert_equal(
            unstack(self.dy_2[:, 0, :])[0], unstack(self.dy_123[:, 0, :])[y_index]
        )

        tf.assert_equal(self.dy_2[:, 1, :], unstack(self.dy_123[:, 1, :])[y_index])
        tf.assert_equal(
            unstack(self.dy_2[:, 1, :])[0], unstack(self.dy_123[:, 1, :])[y_index]
        )

    def test_diagonals(self):
        tf.assert_equal(
            elvet.math.diagonals(self.dy_12, y_index=0),
            self.dy_1[:, 0, :] + self.dy_1[:, 1, :],
        )
        tf.assert_equal(
            elvet.math.diagonals(self.dy_12, y_index=1),
            self.dy_2[:, 0, :] + self.dy_2[:, 1, :],
        )
        tf.assert_equal(
            elvet.math.diagonals(self.dy_123, y_index=2),
            self.dy_3[:, 0, :] + self.dy_3[:, 1, :],
        )

    def test_curl(self):
        fx3D_123 = lambda x: tf.reshape(
            tf.stack(
                [
                    unstack(x)[0] ** 2 + unstack(x)[1] ** 3 + unstack(x)[2] * 2,
                    unstack(x)[0] ** 3 + unstack(x)[1] + unstack(x)[2],
                    unstack(x)[0] ** 5 * unstack(x)[1] ** 2 + unstack(x)[2] * 3,
                ],
                axis=1,
            ),
            (x.shape[0], 3),
        )
        x3D = elvet.constant([[1.0, 2.0, 5.0], [3.0, 4.0, 6.0]])
        dy3D_1 = elvet.math.derivative(fx3D_123, x3D, 1)
        tf.assert_equal(
            elvet.math.curl(dy3D_1),
            elvet.constant([[3.0, 1.943e3], [-1.8e1, -6.478e3], [-9.0, -2.1e1]]),
        )

    def test_second_derivative(self):
        y_index = 0
        tf.assert_equal(
            self.d2y_1[:, 0, 0, :], unstack(self.d2y_12[:, 0, 0, :])[y_index]
        )
        tf.assert_equal(
            self.d2y_1[:, 1, 1, :], unstack(self.d2y_12[:, 1, 1, :])[y_index]
        )

        y_index = 1
        tf.assert_equal(
            self.d2y_2[:, 0, 0, :], unstack(self.d2y_12[:, 0, 0, :])[y_index]
        )
        tf.assert_equal(
            self.d2y_2[:, 0, 1, :], unstack(self.d2y_12[:, 0, 1, :])[y_index]
        )

        tf.assert_equal(self.d2y_3[:, 0, 0, :], unstack(self.d2y_123[:, 0, 0, :])[2])
        tf.assert_equal(self.d2y_3[:, 0, 1, :], unstack(self.d2y_123[:, 0, 1, :])[2])
        tf.assert_equal(self.d2y_3[:, 1, 1, :], unstack(self.d2y_123[:, 1, 1, :])[2])

    def test_laplacian(self):
        tf.assert_equal(
            tf.reshape(
                tf.stack(
                    [
                        elvet.math.laplacian(self.d2y_1),
                        elvet.math.laplacian(self.d2y_2),
                        elvet.math.laplacian(self.d2y_3),
                    ],
                    axis=1,
                ),
                (2, 3),
            ),
            elvet.math.laplacian(self.d2y_123),
        )

        tf.assert_equal(
            elvet.math.laplacian(self.d2y_1),
            elvet.math.laplacian(self.d2y_12, y_index=0),
        )
        tf.assert_equal(
            elvet.math.laplacian(self.d2y_2),
            elvet.math.laplacian(self.d2y_12, y_index=1),
        )
        tf.assert_equal(
            elvet.math.laplacian(self.d2y_3),
            elvet.math.laplacian(self.d2y_123, y_index=2),
        )

    def test_laplace_beltrami(self):
        tf.assert_equal(
            elvet.math.laplace_beltrami(
                self.d2y_1,
                metric="mostlyminus",
                c=elvet.speed_of_light_m_s,
                time_domain=0,
            ),
            1 / elvet.speed_of_light_m_s ** 2 * self.d2y_1[:, 0, 0, :]
            - self.d2y_1[:, 1, 1, :],
        )
        tf.assert_equal(
            elvet.math.laplace_beltrami(
                self.d2y_1,
                metric="mostlyminus",
                c=elvet.speed_of_light_m_s,
                time_domain=1,
            ),
            -self.d2y_1[:, 0, 0, :]
            + 1 / elvet.speed_of_light_m_s ** 2 * self.d2y_1[:, 1, 1, :],
        )

        tf.assert_equal(
            elvet.math.laplace_beltrami(
                self.d2y_1,
                metric="mostlyplus",
                c=elvet.speed_of_light_m_s,
                time_domain=0,
            ),
            -1 / elvet.speed_of_light_m_s ** 2 * self.d2y_1[:, 0, 0, :]
            + self.d2y_1[:, 1, 1, :],
        )
        tf.assert_equal(
            elvet.math.laplace_beltrami(
                self.d2y_1,
                metric="mostlyplus",
                c=elvet.speed_of_light_m_s,
                time_domain=1,
            ),
            self.d2y_1[:, 0, 0, :]
            - 1 / elvet.speed_of_light_m_s ** 2 * self.d2y_1[:, 1, 1, :],
        )

        tf.assert_equal(
            elvet.math.laplace_beltrami(
                self.d2y_1,
                metric="mostlyplus",
                c=elvet.speed_of_light_m_s,
                time_domain=0,
            ),
            elvet.math.laplace_beltrami(
                self.d2y_12,
                y_index=0,
                metric="mostlyplus",
                c=elvet.speed_of_light_m_s,
                time_domain=0,
            ),
        )
        tf.assert_equal(
            elvet.math.laplace_beltrami(
                self.d2y_2,
                metric="mostlyplus",
                c=elvet.speed_of_light_m_s,
                time_domain=1,
            ),
            elvet.math.laplace_beltrami(
                self.d2y_12,
                y_index=1,
                metric="mostlyplus",
                c=elvet.speed_of_light_m_s,
                time_domain=1,
            ),
        )

    def test_delambertian(self):
        tf.assert_equal(
            elvet.math.dalembertian(
                self.d2y_12, y_index=0, c=elvet.speed_of_light_m_s, time_domain=1
            ),
            -self.d2y_1[:, 0, 0, :]
            + 1 / elvet.speed_of_light_m_s ** 2 * self.d2y_1[:, 1, 1, :],
        )

        tf.assert_equal(
            elvet.math.dalembertian(
                self.d2y_12, y_index=1, c=elvet.speed_of_light_m_s, time_domain=0
            ),
            1 / elvet.speed_of_light_m_s ** 2 * self.d2y_2[:, 0, 0, :]
            - self.d2y_2[:, 1, 1, :],
        )


if __name__ == "__main__":
    unittest.main()
