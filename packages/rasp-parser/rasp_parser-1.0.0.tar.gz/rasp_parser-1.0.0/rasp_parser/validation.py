"""
Validation functionality for RASP motor data
"""

from typing import List

from rasp_parser.exceptions import RASPValidationError
from rasp_parser.models import RASPMotor


class MotorValidator:
    """Validator for RASP motor data"""

    @staticmethod
    def validate_motor(motor: RASPMotor, strict: bool = False) -> List[str]:
        """
        Validate a parsed motor and return a list of warnings/issues

        Args:
            motor: The RASPMotor to validate
            strict: If True, raise exception on validation errors

        Returns:
            List of validation warnings (empty if no issues)

        Raises:
            RASPValidationError: If strict=True and validation fails
        """
        warnings = []

        # Check basic data consistency
        warnings.extend(MotorValidator._validate_basic_data(motor))

        # Check thrust curve
        warnings.extend(MotorValidator._validate_thrust_curve(motor))

        if strict and warnings:
            raise RASPValidationError(
                f"Motor validation failed {len(warnings)} issues: "
                + "; ".join(warnings)
            )

        return warnings

    @staticmethod
    def _validate_basic_data(motor: RASPMotor) -> List[str]:
        """Validate basic motor data"""
        warnings = []

        if motor.total_mass <= motor.propellant_mass:
            warnings.append("Total mass should be greater than propellant mass")

        if motor.diameter <= 0:
            warnings.append("Diameter should be positive")

        if motor.length <= 0:
            warnings.append("Length should be positive")

        if motor.propellant_mass <= 0:
            warnings.append("Propellant mass should be positive")

        if motor.total_mass <= 0:
            warnings.append("Total mass should be positive")

        # Check calculated properties
        if motor.total_impulse <= 0:
            warnings.append("Total impulse should be positive")

        if motor.peak_thrust <= 0:
            warnings.append("Peak thrust should be positive")

        # Reasonable ranges check
        if motor.diameter > 500:  # 500mm is very large
            warnings.append(f"Diameter ({motor.diameter}mm) seems unusually large")

        if motor.length > 5000:  # 5m is very long
            warnings.append(f"Length ({motor.length}mm) seems unusually long")

        return warnings

    @staticmethod
    def _validate_thrust_curve(motor: RASPMotor) -> List[str]:
        """Validate thrust curve data"""
        warnings = []

        if not motor.thrust_curve:
            warnings.append("No thrust curve data found")
            return warnings

        # Check for minimum data points
        if len(motor.thrust_curve) < 3:
            warnings.append(
                f"Very sparse thrust curve data ({len(motor.thrust_curve)} " "points)"
            )

        # Check for monotonic time values
        times = [point.time for point in motor.thrust_curve]
        if times != sorted(times):
            warnings.append(
                "Thrust curve time values are not " "monotonically increasing"
            )

        # Check if thrust curve starts at t=0 or near 0
        if times[0] > 0.1:
            warnings.append(f"Thrust curve starts at t={times[0]:.3f}s, not near zero")

        # Check if thrust curve ends at zero thrust
        if motor.thrust_curve[-1].thrust > 0.1:
            warnings.append("Thrust curve does not end at zero thrust")

        # Check for negative values
        for i, point in enumerate(motor.thrust_curve):
            if point.time < 0:
                warnings.append(f"Negative time value at point {i}: {point.time}s")
            if point.thrust < 0:
                warnings.append(f"Negative thrust value at point {i}: {point.thrust}N")

        # Verify peak thrust matches curve
        max_curve_thrust = max(point.thrust for point in motor.thrust_curve)
        if abs(max_curve_thrust - motor.peak_thrust) > 0.01 * motor.peak_thrust:
            warnings.append(
                f"Peak thrust in header ({motor.peak_thrust:.1f}N) does"
                f"not match curve maximum ({max_curve_thrust:.1f}N)"
            )

        return warnings


# Convenience function
def validate_motor(motor: RASPMotor, strict: bool = False) -> List[str]:
    """Validate a RASP motor - convenience function"""
    return MotorValidator.validate_motor(motor, strict)
