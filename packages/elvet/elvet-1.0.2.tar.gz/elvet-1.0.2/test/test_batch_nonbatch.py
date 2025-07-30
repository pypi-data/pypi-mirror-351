import unittest
import elvet


class TestDiffOps(unittest.TestCase):
    def setUp(self):
        def eqn_batch(x, y, dy, dy2):
            return dy2[0, 0, 0] + dy[0, 1]

        def eqn(x, y, dy, dy2):
            return elvet.unstack(dy2[:, 0, 0, :])[0] + elvet.unstack(dy[:, 0, :])[1]

        self.domain = elvet.box((0, 1, 10), (0, 1, 10))
        bc1_batch = elvet.BC(0, lambda x, y, dy, dy2: y[0])
        bc2_batch = bc1_batch
        bc3_batch = bc1_batch
        bc4_batch = bc1_batch

        bc1 = elvet.BC(0, lambda x, y, dy, dy2: elvet.unstack(y)[0])
        bc2 = bc1
        bc3 = bc1
        bc4 = bc1

        self.batch_mode_solver = elvet.solver(
            eqn, (bc1, bc2, bc3, bc4), self.domain, batch=True, model=elvet.nn(2, 10, 2)
        )
        self.nonbatch_mode_solver = elvet.solver(
            eqn_batch,
            (bc1_batch, bc2_batch, bc3_batch, bc4_batch),
            self.domain,
            model=elvet.nn(2, 10, 2),
        )

        def test_shapes(self):
            batch_mode = self.batch_mode_solver.functional(
                self.domain, *self.batch_mode_solver.derivatives(self.domain)
            )
            nonbatch_mode = self.nonbatch_mode_solver.functional(
                self.domain, *self.nonbatch_mode_solver.derivatives(self.domain)
            )

            assert batch_mode[0][0].numpy().shape == nonbatch_mode[0][0].numpy().shape + (1,)
            assert batch_mode[1][0].numpy().shape == nonbatch_mode[1][0].numpy().shape + (1,)


if __name__ == "__main__":
    unittest.main()
