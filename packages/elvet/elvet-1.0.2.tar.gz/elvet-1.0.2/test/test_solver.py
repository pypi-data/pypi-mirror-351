import unittest

import numpy as np

import elvet


class TestSolver(unittest.TestCase):
    def test_solver(self):
        def equations(x, y, dy):
            A = (1 + 3 * x ** 2) / (1 + x + x ** 3)
            return dy + (x + A) * y - x ** 3 - 2 * x - x ** 2 * A

        bc = elvet.BC(0, lambda x, y, dy: y - 1)
        domain = elvet.box((0, 2, 100))

        model = elvet.nn(1, 10, 1)

        x = domain.numpy()
        y_truth = np.exp(-0.5 * x ** 2) / (1 + x + x ** 3) + x ** 2
        mse = elvet.utils.metrics.MSE(y_truth)

        solver = elvet.solver(
            equations=equations,
            bcs=bc,
            domain=domain,
            model=model,
            optimizer="sgd",
            lr=1e-2,
            metrics=[elvet.utils.metrics.WatchLR(), mse],
        )
        solver.fit(50000, verbose=True)

        y = solver.prediction()

        assert (
            (y - y_truth) ** 2
        ).mean() < 1.0, "sum((y - y_truth)**2) = {:.5f}".format(
            ((y - y_truth) ** 2).mean()
        )


if __name__ == "__main__":
    unittest.main()
