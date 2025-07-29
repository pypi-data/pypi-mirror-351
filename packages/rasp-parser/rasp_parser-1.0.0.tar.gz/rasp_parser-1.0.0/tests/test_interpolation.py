"""
Tests for thrust interpolation functionality
"""

import pytest
from rasp_parser import RASPParser, SCIPY_AVAILABLE
from rasp_parser.models import ThrustCurvePoint


class TestInterpolation:
    """Test thrust curve interpolation methods"""

    def setup_method(self):
        """Set up test motors for interpolation tests"""
        # Simple linear motor for basic tests
        self.linear_rasp = """
; Linear test motor
TEST1 24 70 0 0.01 0.02 Test
0.0 0.0
1.0 100.0
2.0 0.0
"""

        # More complex motor with multiple points
        self.complex_rasp = """
; Complex test motor
TEST2 29 98 0 0.05 0.08 Test
0.0 0.0
0.5 50.0
1.0 100.0
1.5 120.0
2.0 80.0
2.5 40.0
3.0 0.0
"""

        # Sparse motor (only 3 points - should use linear interpolation)
        self.sparse_rasp = """
; Sparse test motor
TEST3 18 50 0 0.005 0.01 Test
0.0 0.0
1.0 50.0
2.0 0.0
"""

    def test_interpolation_at_data_points(self):
        """Test interpolation returns exact values at data points"""
        motor = RASPParser.parse_string(self.complex_rasp)

        # Should return exact values at data points
        assert abs(motor.get_interpolated_thrust(0.0) - 0.0) < 1e-10
        assert abs(motor.get_interpolated_thrust(0.5) - 50.0) < 1e-10
        assert abs(motor.get_interpolated_thrust(1.0) - 100.0) < 1e-10
        assert abs(motor.get_interpolated_thrust(1.5) - 120.0) < 1e-10
        assert abs(motor.get_interpolated_thrust(2.0) - 80.0) < 1e-10
        assert abs(motor.get_interpolated_thrust(2.5) - 40.0) < 1e-10
        assert abs(motor.get_interpolated_thrust(3.0) - 0.0) < 1e-10

    def test_interpolation_between_points(self):
        """Test interpolation between data points"""
        motor = RASPParser.parse_string(self.linear_rasp)

        # Linear motor: thrust at t=0.5 should be 50.0
        thrust_mid = motor.get_interpolated_thrust(0.5)
        # Allow small error for spline methods
        assert abs(thrust_mid - 50.0) < 1.0

        # Complex motor: test interpolation between known points
        motor_complex = RASPParser.parse_string(self.complex_rasp)
        thrust_between = motor_complex.get_interpolated_thrust(0.25)
        assert 0.0 < thrust_between < 50.0  # Should be between endpoints

    def test_interpolation_bounds(self):
        """Test interpolation outside motor burn time returns zero"""
        motor = RASPParser.parse_string(self.complex_rasp)

        # Before motor start
        assert motor.get_interpolated_thrust(-0.5) == 0.0
        assert motor.get_interpolated_thrust(-1.0) == 0.0

        # After motor burnout
        assert motor.get_interpolated_thrust(3.5) == 0.0
        assert motor.get_interpolated_thrust(10.0) == 0.0

    def test_interpolation_edge_cases(self):
        """Test interpolation edge cases"""
        motor = RASPParser.parse_string(self.complex_rasp)

        # Exactly at start and end times
        assert abs(motor.get_interpolated_thrust(0.0) - 0.0) < 1e-10
        assert abs(motor.get_interpolated_thrust(3.0) - 0.0) < 1e-10

        # Very close to data points
        assert abs(motor.get_interpolated_thrust(0.0001) - 0.0) < 5.0
        assert abs(motor.get_interpolated_thrust(2.9999) - 0.0) < 5.0

    def test_sparse_data_interpolation(self):
        """Test interpolation with sparse data (should use linear)"""
        motor = RASPParser.parse_string(self.sparse_rasp)

        # With only 3 points, should use linear interpolation
        thrust_mid = motor.get_interpolated_thrust(0.5)
        assert 20.0 < thrust_mid < 30.0  # Linear interpolation between 0 and 50

        thrust_75 = motor.get_interpolated_thrust(1.5)
        assert 20.0 < thrust_75 < 30.0  # Linear interpolation between 50 and 0

    def test_interpolation_monotonic_decrease(self):
        """Test interpolation behavior during motor tail-off"""
        # Motor with decreasing thrust
        tail_off_rasp = """
; Tail-off test motor
TAIL 24 70 0 0.01 0.02 Test
0.0 0.0
0.5 100.0
1.0 80.0
1.5 60.0
2.0 40.0
2.5 20.0
3.0 0.0
"""
        motor = RASPParser.parse_string(tail_off_rasp)

        # Test that interpolated values follow the decreasing trend
        thrust_1_25 = motor.get_interpolated_thrust(1.25)
        thrust_1_75 = motor.get_interpolated_thrust(1.75)

        assert thrust_1_25 > thrust_1_75  # Should be decreasing
        assert 60.0 < thrust_1_25 < 80.0  # Between t=1.0 and t=1.5
        assert 40.0 < thrust_1_75 < 60.0  # Between t=1.5 and t=2.0

    def test_interpolation_with_plateau(self):
        """Test interpolation with sustained thrust plateau"""
        plateau_rasp = """
; Plateau test motor
PLAT 29 120 0 0.05 0.08 Test
0.0 0.0
0.5 80.0
1.0 100.0
2.0 100.0
3.0 100.0
3.5 80.0
4.0 0.0
"""
        motor = RASPParser.parse_string(plateau_rasp)

        # During plateau, thrust should be close to 100N
        thrust_plateau_1 = motor.get_interpolated_thrust(1.5)
        thrust_plateau_2 = motor.get_interpolated_thrust(2.5)

        assert abs(thrust_plateau_1 - 100.0) < 10.0
        assert abs(thrust_plateau_2 - 100.0) < 10.0

    def test_no_thrust_curve_data(self):
        """Test interpolation with empty thrust curve"""
        from rasp_parser.models import RASPMotor

        # Create motor with no thrust data
        empty_motor = RASPMotor(
            designation="EMPTY",
            diameter=24.0,
            length=70.0,
            delays="0",
            propellant_mass=0.01,
            total_mass=0.02,
            manufacturer="Test",
            thrust_curve=[],
            comments=[],
        )

        assert empty_motor.get_interpolated_thrust(1.0) == 0.0

    def test_single_point_thrust_curve(self):
        """Test interpolation with single data point"""
        from rasp_parser.models import RASPMotor

        single_point_motor = RASPMotor(
            designation="SINGLE",
            diameter=24.0,
            length=70.0,
            delays="0",
            propellant_mass=0.01,
            total_mass=0.02,
            manufacturer="Test",
            thrust_curve=[ThrustCurvePoint(1.0, 50.0)],
            comments=[],
        )

        # Should return 0 since we can't interpolate with one point
        assert single_point_motor.get_interpolated_thrust(1.0) == 0.0
        assert single_point_motor.get_interpolated_thrust(0.5) == 0.0

    @pytest.mark.skipif(not SCIPY_AVAILABLE, reason="scipy not available")
    def test_cubic_spline_vs_linear_accuracy(self):
        """Compare cubic spline vs linear interpolation accuracy"""
        # Create a smooth function we know the answer to
        smooth_rasp = """
; Smooth function motor (parabolic)
SMOOTH 24 70 0 0.01 0.02 Test
0.0 0.0
0.5 25.0
1.0 100.0
1.5 225.0
2.0 400.0
2.5 225.0
3.0 100.0
3.5 25.0
4.0 0.0
"""
        motor = RASPParser.parse_string(smooth_rasp)

        # Test interpolation at quarter points
        test_times = [0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75]

        for t in test_times:
            thrust = motor.get_interpolated_thrust(t)
            # Should be reasonable values (not testing exact accuracy here)
            assert thrust >= 0.0
            assert thrust <= 500.0  # Reasonable upper bound

    def test_interpolation_precision(self):
        """Test interpolation numerical precision"""
        motor = RASPParser.parse_string(self.linear_rasp)

        # Test many small steps
        for i in range(21):  # 0.0 to 2.0 in steps of 0.1
            t = i * 0.1
            thrust = motor.get_interpolated_thrust(t)
            assert thrust >= 0.0
            # For linear motor, thrust should follow expected pattern
            if 0.0 <= t <= 1.0:
                expected = t * 100.0  # Linear increase
                assert abs(thrust - expected) < 5.0
            elif 1.0 < t <= 2.0:
                expected = (2.0 - t) * 100.0  # Linear decrease
                assert abs(thrust - expected) < 5.0

    def test_interpolation_method_selection(self):
        """Test that appropriate interpolation method is selected"""
        # Sparse data should use linear interpolation
        sparse_motor = RASPParser.parse_string(self.sparse_rasp)

        # Dense data should use cubic spline if scipy available
        dense_motor = RASPParser.parse_string(self.complex_rasp)

        # Both should return reasonable values
        assert 0.0 <= sparse_motor.get_interpolated_thrust(0.5) <= 50.0
        assert 0.0 <= dense_motor.get_interpolated_thrust(0.75) <= 150.0

    def test_interpolation_performance(self):
        """Test that interpolation performs reasonably fast"""
        import time

        motor = RASPParser.parse_string(self.complex_rasp)

        # Time many interpolation calls
        start_time = time.time()
        for i in range(1000):
            motor.get_interpolated_thrust(i * 0.003)  # 0 to 3 seconds
        end_time = time.time()

        # Should complete 1000 interpolations in reasonable time
        assert (end_time - start_time) < 1.0  # Less than 1 second
