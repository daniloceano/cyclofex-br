#!/usr/bin/env python3
"""Automated geometry checks for E-001 (standard-library unittest)."""

from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e001_orientation import (  # noqa: E402
    compute_motion,
    inverse_rotate_motion,
    local_xy_km,
    rotate_motion,
)


class CoordinateTests(unittest.TestCase):
    def test_center_is_origin(self) -> None:
        x, y = local_xy_km(-35.0, -45.0, -35.0, -45.0)
        self.assertAlmostEqual(float(x), 0.0, places=12)
        self.assertAlmostEqual(float(y), 0.0, places=12)

    def test_cardinal_signs(self) -> None:
        east_x, east_y = local_xy_km(-35.0, -45.0, -35.0, -44.0)
        north_x, north_y = local_xy_km(-35.0, -45.0, -34.0, -45.0)
        self.assertGreater(float(east_x), 0.0)
        # On the sphere, the shortest path between equal-latitude endpoints
        # is not the geographic parallel; its meridional component is small.
        self.assertLess(abs(float(east_y)), 1.0)
        self.assertAlmostEqual(float(north_x), 0.0, places=9)
        self.assertGreater(float(north_y), 0.0)

    def test_forward_and_right_for_eastward_heading(self) -> None:
        heading_east = np.array([np.pi / 2.0, np.pi / 2.0])
        # East is forward; south is right when moving east.
        xm, ym = rotate_motion(
            np.array([100.0, 0.0]),
            np.array([0.0, -100.0]),
            heading_east,
        )
        np.testing.assert_allclose([xm[0], ym[0]], [0.0, 100.0], atol=1e-12)
        np.testing.assert_allclose([xm[1], ym[1]], [100.0, 0.0], atol=1e-12)

    def test_rotation_preserves_distance_and_is_invertible(self) -> None:
        rng = np.random.default_rng(42)
        x = rng.normal(size=10_000) * 500.0
        y = rng.normal(size=10_000) * 500.0
        heading = rng.uniform(-np.pi, np.pi, size=x.size)
        xm, ym = rotate_motion(x, y, heading)
        recovered_x, recovered_y = inverse_rotate_motion(xm, ym, heading)
        np.testing.assert_allclose(np.hypot(x, y), np.hypot(xm, ym), atol=1e-10)
        np.testing.assert_allclose(x, recovered_x, atol=1e-10)
        np.testing.assert_allclose(y, recovered_y, atol=1e-10)

    def test_heading_uses_track_sequence(self) -> None:
        track_id = np.array([1, 1, 1, 2, 2, 2])
        time_hours = np.array([0.0, 6.0, 12.0, 0.0, 6.0, 12.0])
        latitude = np.array([-35.0, -35.0, -35.0, -36.0, -35.0, -34.0])
        longitude = np.array([-46.0, -45.0, -44.0, -45.0, -45.0, -45.0])
        heading, speed, _, _ = compute_motion(track_id, time_hours, latitude, longitude)
        np.testing.assert_allclose(heading[:3], np.pi / 2.0, atol=0.01)
        np.testing.assert_allclose(heading[3:], 0.0, atol=1e-12)
        self.assertTrue(np.all(speed > 0.0))


if __name__ == "__main__":
    unittest.main()
