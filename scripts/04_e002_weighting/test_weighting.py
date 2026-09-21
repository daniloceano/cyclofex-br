#!/usr/bin/env python3
"""Unit tests for E-002 weighting identities and metrics."""

from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e002_weighting import normalized_rows, probability  # noqa: E402


class WeightingTests(unittest.TestCase):
    def test_equal_cyclone_rows_have_unit_mass(self) -> None:
        state_mass = np.array([[0.25, 0.75, 1.0], [0.0, 0.0, 0.0], [2.0, 1.0, 0.0]], dtype=np.float32)
        counts = np.array([2, 0, 3])
        cyclone_mass = normalized_rows(state_mass, counts)
        np.testing.assert_allclose(cyclone_mass.sum(axis=1), [1.0, 0.0, 1.0])

    def test_equal_state_preserves_state_count_mass(self) -> None:
        state_mass = np.array([[0.25, 0.75, 1.0], [2.0, 1.0, 0.0]], dtype=np.float32)
        np.testing.assert_allclose(state_mass.sum(axis=1), [2.0, 3.0])

    def test_probability_is_normalized(self) -> None:
        values = probability(np.array([[1.0, 2.0], [3.0, 4.0]]))
        self.assertAlmostEqual(float(values.sum()), 1.0)
        np.testing.assert_allclose(values, [0.4, 0.6])

    def test_equal_sized_cyclones_make_weightings_identical(self) -> None:
        state_mass = np.array([[1.0, 1.0], [0.5, 1.5]], dtype=np.float32)
        counts = np.array([2, 2])
        np.testing.assert_allclose(probability(state_mass), probability(normalized_rows(state_mass, counts)))


if __name__ == "__main__":
    unittest.main()
