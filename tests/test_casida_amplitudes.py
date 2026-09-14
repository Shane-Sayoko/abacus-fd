"""Tests for portable Casida-amplitude output from parallel ABACUS runs."""

import os
import tempfile
import unittest

import numpy as np

from abacus_fd.core import merge_parallel_casida_amplitudes


class CasidaAmplitudeMergeTest(unittest.TestCase):
    def test_two_rank_column_distribution(self):
        nstates, nocc, nvirt = 2, 2, 18
        with tempfile.TemporaryDirectory() as directory:
            for rank, base in enumerate((100.0, 200.0)):
                values = np.vstack((base + np.arange(nvirt), base + 100.0 + np.arange(nvirt)))
                np.savetxt(os.path.join(directory, f"Excitation_Amplitude_singlet_{rank}.dat"), values)

            merged = merge_parallel_casida_amplitudes(directory, 2, nstates, nocc, nvirt)
            result = np.loadtxt(merged)
            self.assertEqual(result.shape, (nstates, nocc * nvirt))
            np.testing.assert_allclose(result[0, :nvirt], 100.0 + np.arange(nvirt))
            np.testing.assert_allclose(result[0, nvirt:], 200.0 + np.arange(nvirt))
            np.testing.assert_allclose(result[1, :nvirt], 200.0 + np.arange(nvirt))
            np.testing.assert_allclose(result[1, nvirt:], 300.0 + np.arange(nvirt))

    def test_rejects_truncated_rank_block(self):
        with tempfile.TemporaryDirectory() as directory:
            np.savetxt(os.path.join(directory, "Excitation_Amplitude_singlet_0.dat"), np.zeros((2, 18)))
            np.savetxt(os.path.join(directory, "Excitation_Amplitude_singlet_1.dat"), np.zeros((2, 17)))
            with self.assertRaises(RuntimeError):
                merge_parallel_casida_amplitudes(directory, 2, 2, 2, 18)


if __name__ == "__main__":
    unittest.main()
