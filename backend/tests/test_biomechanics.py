import pytest
import math
from backend.app.analysis.biomechanics import BiomechanicsCalculator

def test_calculate_angle_3d_right_angle():
    # 90 degree angle at vertex B (0,0) with A (1,0) and C (0,1)
    pointA = {"x": 1.0, "y": 0.0, "z": 0.0}
    pointB = {"x": 0.0, "y": 0.0, "z": 0.0}
    pointC = {"x": 0.0, "y": 1.0, "z": 0.0}
    angle = BiomechanicsCalculator.calculate_angle_3d(pointA, pointB, pointC)
    assert abs(angle - 90.0) < 1e-4

def test_calculate_angle_3d_straight_line():
    # 180 degree angle at vertex B (0,0) with A (-1,0) and C (1,0)
    pointA = {"x": -1.0, "y": 0.0, "z": 0.0}
    pointB = {"x": 0.0, "y": 0.0, "z": 0.0}
    pointC = {"x": 1.0, "y": 0.0, "z": 0.0}
    angle = BiomechanicsCalculator.calculate_angle_3d(pointA, pointB, pointC)
    assert abs(angle - 180.0) < 1e-4

def test_calculate_angle_3d_numerical_clamping():
    # Identical vectors (0 degree angle) should handle numerical noise without NaN
    pointA = {"x": 1.0000000000000002, "y": 0.0, "z": 0.0}
    pointB = {"x": 0.0, "y": 0.0, "z": 0.0}
    pointC = {"x": 1.0, "y": 0.0, "z": 0.0}
    angle = BiomechanicsCalculator.calculate_angle_3d(pointA, pointB, pointC)
    assert not math.isnan(angle)
    assert abs(angle - 0.0) < 1e-3

def test_trunk_inclination():
    shoulder = {"x": 0.5, "y": 0.2}
    hip = {"x": 0.5, "y": 0.8}
    # Perfectly upright trunk relative to vertical
    incl = BiomechanicsCalculator.calculate_trunk_inclination(shoulder, hip)
    assert abs(incl) < 1e-3
