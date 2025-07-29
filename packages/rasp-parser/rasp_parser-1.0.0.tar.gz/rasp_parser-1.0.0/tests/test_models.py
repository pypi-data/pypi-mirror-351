"""
Tests for RASP motor data models
"""

import pytest
from rasp_parser.models import RASPMotor, ThrustCurvePoint, SCIPY_AVAILABLE


class TestThrustCurvePoint:
    """Test ThrustCurvePoint data model"""

    def test_thrust_curve_point_creation(self):
        """Test creating thrust curve points"""
        point = ThrustCurvePoint(1.5, 125.7)
        assert point.time == 1.5
        assert point.thrust == 125.7

    def test_thrust_curve_point_str(self):
        """Test string representation of thrust curve point"""
        point = ThrustCurvePoint(2.345, 98.76)
        str_repr = str(point)
        assert "2.345s" in str_repr
        assert "98.760N" in str_repr


class TestRASPMotor:
    """Test RASPMotor data model"""

    def setup_method(self):
        """Set up test motor data using real Estes D12 RASP data"""
        # Real Estes D12 data from NAR certification
        d12_rasp = """
    ;Estes D12 RASP.ENG file made from NAR published data
    ;File produced October 3, 2000
    ;The total impulse, peak thrust, average thrust and burn time are
    ;the same as the averaged static test data on the NAR web site in
    ;the certification file. The curve drawn with these data points is as
    ;close to the certification curve as can be with such a limited
    ;number of points (32) allowed with wRASP up to v1.6.
    D12 24 70 0-3-5-7 0.0211 0.0426 Estes
    0.049 2.569
    0.116 9.369
    0.184 17.275
    0.237 24.258
    0.282 29.73
    0.297 27.01
    0.311 22.589
    0.322 17.99
    0.348 14.126
    0.386 12.099
    0.442 10.808
    0.546 9.876
    0.718 9.306
    0.879 9.105
    1.066 8.901
    1.257 8.698
    1.436 8.31
    1.59 8.294
    1.612 4.613
    1.65 0
    """
        from rasp_parser import RASPParser

        self.motor = RASPParser.parse_string(d12_rasp)

        # Simple test points for basic tests
        self.thrust_points = [
            ThrustCurvePoint(0.0, 0.0),
            ThrustCurvePoint(0.5, 50.0),
            ThrustCurvePoint(1.0, 100.0),
            ThrustCurvePoint(1.5, 80.0),
            ThrustCurvePoint(2.0, 0.0),
        ]

    def test_motor_creation(self):
        """Test creating a RASP motor"""
        assert self.motor.designation == "D12"
        assert self.motor.diameter == 24.0
        assert self.motor.manufacturer == "Estes"
        assert len(self.motor.thrust_curve) == 20

    def test_burn_time_calculation(self):
        """Test burn time calculation"""
        assert self.motor.burn_time == 1.65

    def test_peak_thrust_calculation(self):
        """Test peak thrust calculation"""
        assert abs(self.motor.peak_thrust - 29.73) < 0.1

    def test_total_impulse_calculation(self):
        """Test total impulse calculation"""
        # Should be > 0 and reasonable for this motor
        assert self.motor.total_impulse > 0
        assert self.motor.total_impulse < 500  # Reasonable upper bound

    def test_average_thrust_calculation(self):
        """Test average thrust calculation"""
        avg_thrust = self.motor.average_thrust
        assert avg_thrust > 0
        assert avg_thrust == self.motor.total_impulse / self.motor.burn_time

    def test_impulse_class_calculation(self):
        """Test impulse class determination"""
        impulse_class = self.motor.impulse_class
        assert impulse_class in "D"

        # Test specific ranges
        low_impulse_motor = RASPMotor(
            designation="A8",
            diameter=18.0,
            length=50.0,
            delays="3",
            propellant_mass=0.002,
            total_mass=0.008,
            manufacturer="Estes",
            thrust_curve=[
                ThrustCurvePoint(0.0, 0.0),
                ThrustCurvePoint(0.5, 4.0),
                ThrustCurvePoint(1.0, 0.0),
            ],
            comments=[],
        )
        assert low_impulse_motor.impulse_class in "ABC"

    def test_specific_impulse_calculation(self):
        """Test specific impulse calculation with real D12 data"""
        isp = self.motor.specific_impulse
        assert isp > 0

        assert 80 < isp < 120  # Realistic range for Estes solid motors
        print(f"D12 Specific Impulse: {isp:.1f} seconds")

        # Test with zero propellant mass
        zero_prop_motor = RASPMotor(
            designation="TEST",
            diameter=24.0,
            length=70.0,
            delays="0",
            propellant_mass=0.0,
            total_mass=0.02,
            manufacturer="Test",
            thrust_curve=self.thrust_points,
            comments=[],
        )
        assert zero_prop_motor.specific_impulse == 0.0

    def test_motor_string_representation(self):
        """Test motor string representation"""
        motor_str = str(self.motor)

        assert "D12" in motor_str
        assert "Estes" in motor_str
        assert "24" in motor_str  # Diameter
        assert "70" in motor_str  # Length
        assert "Class:" in motor_str
        assert "Total Impulse:" in motor_str
        assert "Peak Thrust:" in motor_str

    def test_empty_thrust_curve(self):
        """Test motor with empty thrust curve"""
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

        assert empty_motor.burn_time == 0.0
        assert empty_motor.peak_thrust == 0.0
        assert empty_motor.total_impulse == 0.0
        assert empty_motor.average_thrust == 0.0

    def test_single_point_thrust_curve(self):
        """Test motor with single thrust point"""
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

        assert single_point_motor.burn_time == 1.0
        assert single_point_motor.peak_thrust == 50.0
        assert single_point_motor.total_impulse == 0.0  # Can't integrate single point

    def test_integration_methods(self):
        """Test different integration methods"""
        # Create motor with enough points for cubic spline
        many_points = [ThrustCurvePoint(i * 0.2, 50.0 + i * 10.0) for i in range(10)]
        many_points.append(ThrustCurvePoint(2.0, 0.0))

        complex_motor = RASPMotor(
            designation="COMPLEX",
            diameter=29.0,
            length=98.0,
            delays="6",
            propellant_mass=0.05,
            total_mass=0.08,
            manufacturer="Test",
            thrust_curve=many_points,
            comments=[],
        )

        # Should use cubic spline if scipy available, otherwise Simpson's
        total_impulse = complex_motor.total_impulse
        assert total_impulse > 0
        assert total_impulse < 1000  # Reasonable bound

    @pytest.mark.skipif(not SCIPY_AVAILABLE, reason="scipy not available")
    def test_scipy_integration_accuracy(self):
        """Test that scipy integration gives reasonable results"""
        # Create a motor with a known mathematical function
        # Using a parabolic thrust curve: f(t) = -25*t^2 + 50*t for t in [0,2]
        parabolic_points = []
        for i in range(21):  # 0 to 2 seconds in 0.1s steps
            t = i * 0.1
            thrust = max(0, -25 * t * t + 50 * t)
            parabolic_points.append(ThrustCurvePoint(t, thrust))

        parabolic_motor = RASPMotor(
            designation="PARABOLIC",
            diameter=24.0,
            length=70.0,
            delays="0",
            propellant_mass=0.02,
            total_mass=0.04,
            manufacturer="Test",
            thrust_curve=parabolic_points,
            comments=[],
        )

        # Analytical integral of -25*t^2 + 50*t from 0 to 2 is about 33.33
        calculated_impulse = parabolic_motor.total_impulse
        expected_impulse = 33.33

        # Allow for numerical integration errors
        assert abs(calculated_impulse - expected_impulse) < 0.1

    def test_interpolation_basic(self):
        """Test basic interpolation functionality"""
        # Test at data points
        assert abs(self.motor.get_interpolated_thrust(0.049) - 2.569) < 0.1
        assert (
            abs(self.motor.get_interpolated_thrust(0.282) - 29.73) < 0.1
        )  # Peak thrust point
        assert abs(self.motor.get_interpolated_thrust(1.65) - 0.0) < 1e-10  # End point

        # Test between points
        thrust_mid = self.motor.get_interpolated_thrust(0.2)
        assert 10.0 < thrust_mid < 25.0

    def test_interpolation_bounds(self):
        """Test interpolation outside bounds returns zero"""
        assert self.motor.get_interpolated_thrust(-1.0) == 0.0
        assert self.motor.get_interpolated_thrust(3.0) == 0.0

    def test_interpolation_edge_cases(self):
        """Test interpolation edge cases"""
        # Empty thrust curve
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

        # Single point
        single_motor = RASPMotor(
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
        assert (
            single_motor.get_interpolated_thrust(1.0) == 0.0
        )  # Can't interpolate single point

    def test_negative_thrust_handling(self):
        """Test that interpolation doesn't return negative thrust"""
        # Create motor with potential for negative interpolation
        tricky_points = [
            ThrustCurvePoint(0.0, 0.0),
            ThrustCurvePoint(0.5, 100.0),
            ThrustCurvePoint(1.0, 0.0),
            ThrustCurvePoint(1.5, 100.0),
            ThrustCurvePoint(2.0, 0.0),
        ]

        tricky_motor = RASPMotor(
            designation="TRICKY",
            diameter=24.0,
            length=70.0,
            delays="0",
            propellant_mass=0.01,
            total_mass=0.02,
            manufacturer="Test",
            thrust_curve=tricky_points,
            comments=[],
        )

        # Test many interpolation points
        for i in range(21):
            t = i * 0.1
            thrust = tricky_motor.get_interpolated_thrust(t)
            assert thrust >= 0.0  # Should never be negative
