"""
Data models for RASP motor files
"""

from dataclasses import dataclass
from typing import List

try:
    from scipy.interpolate import UnivariateSpline

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


@dataclass
class ThrustCurvePoint:
    """Represents a single point in the thrust curve (time, thrust)"""

    time: float
    thrust: float

    def __str__(self) -> str:
        return f"({self.time:.3f}s, {self.thrust:.3f}N)"


@dataclass
class RASPMotor:
    """Represents a complete RASP motor with all its data"""

    # Header information
    designation: str
    diameter: float  # mm
    length: float  # mm
    delays: str
    propellant_mass: float  # kg
    total_mass: float  # kg (initial weight)
    manufacturer: str

    # Thrust curve data
    thrust_curve: List[ThrustCurvePoint]

    # Comments from the file
    comments: List[str]

    @property
    def total_impulse(self) -> float:
        """
        Calculate total impulse from thrust curve using
        cubic spline integration
        """
        if not self.thrust_curve or len(self.thrust_curve) < 2:
            return 0.0

        if SCIPY_AVAILABLE and len(self.thrust_curve) >= 3:
            return self._cubic_spline_integration()
        else:
            # Fallback to Simpson's rule if scipy not available or
            # insufficient data
            return self._adaptive_simpsons_integration()

    def _cubic_spline_integration(self) -> float:
        """
        Cubic spline integration using scipy - most accurate method
        Creates a smooth cubic spline through the data points and integrates
        analytically
        """
        times = [point.time for point in self.thrust_curve]
        thrusts = [point.thrust for point in self.thrust_curve]

        # Need at least 4 points for cubic spline to work reliably
        if len(self.thrust_curve) < 4:
            return self._adaptive_simpsons_integration()

        try:
            # Create cubic spline (s=0 means interpolation, not smoothing)
            spline = UnivariateSpline(times, thrusts, s=0)

            # Integrate the spline from start to end time
            # The integral method returns the definite integral value
            integral_value = spline.integral(times[0], times[-1])
            return float(integral_value)
        except (ValueError, RuntimeError, TypeError):
            # Fallback to Simpson's if spline fails
            return self._adaptive_simpsons_integration()

    def _adaptive_simpsons_integration(self) -> float:
        """
        Fallback adaptive Simpson's rule integration
        Used when scipy is not available or for very sparse data
        """
        if len(self.thrust_curve) < 2:
            return 0.0

        total = 0.0
        i = 0
        n = len(self.thrust_curve)

        # Process pairs of intervals using Simpson's 1/3 rule
        while i + 2 < n:
            t0, f0 = self.thrust_curve[i].time, self.thrust_curve[i].thrust
            t1, f1 = self.thrust_curve[i + 1].time, self.thrust_curve[i + 1].thrust
            t2, f2 = self.thrust_curve[i + 2].time, self.thrust_curve[i + 2].thrust

            # Simpson's 1/3 rule: ∫f(x)dx ≈ (h/3)[f(x₀) + 4f(x₁) + f(x₂)]
            h = (t2 - t0) / 2
            total += h * (f0 + 4 * f1 + f2) / 3
            i += 2

        # Handle remaining interval(s) with trapezoidal rule
        while i + 1 < n:
            t1, f1 = self.thrust_curve[i].time, self.thrust_curve[i].thrust
            t2, f2 = self.thrust_curve[i + 1].time, self.thrust_curve[i + 1].thrust
            total += (t2 - t1) * (f1 + f2) / 2
            i += 1

        return total

    def get_interpolated_thrust(self, time: float) -> float:
        """
        Get interpolated thrust value at any time point using cubic spline
        Useful for generating smooth thrust curves or getting thrust at
        specific times
        """
        if not self.thrust_curve or len(self.thrust_curve) < 2:
            return 0.0

        times = [point.time for point in self.thrust_curve]
        thrusts = [point.thrust for point in self.thrust_curve]

        # Check bounds - return - outside motor burn time
        if time < times[0] or time > times[-1]:
            return 0.0

        if SCIPY_AVAILABLE and len(self.thrust_curve) >= 4:
            try:
                spline = UnivariateSpline(times, thrusts, s=0)
                result = float(spline(time))
                # Ensure no negative thrust values
                return max(0.0, result)
            except (ValueError, RuntimeError, TypeError):
                pass  # Fall through to linear interpolation

        # Linear interpolation fallback
        for i in range(len(times) - 1):
            if times[i] <= time <= times[i + 1]:
                t1, f1 = times[i], thrusts[i]
                t2, f2 = times[i + 1], thrusts[i + 1]
                return f1 + (f2 - f1) * (time - t1) / (t2 - t1)
        return 0.0

    @property
    def peak_thrust(self) -> float:
        """Calculate peak thrust from thrust curve"""
        if not self.thrust_curve:
            return 0.0
        return max(point.thrust for point in self.thrust_curve)

    @property
    def burn_time(self) -> float:
        """Calculate the burn time from the thrust curve"""
        if not self.thrust_curve:
            return 0.0
        return max(point.time for point in self.thrust_curve)

    @property
    def average_thrust(self) -> float:
        """Calculate average thrust over burn time"""
        if self.burn_time == 0:
            return 0.0
        return self.total_impulse / self.burn_time

    @property
    def impulse_class(self) -> str:
        """
        Determining the impulse class (A, B, C, etc.) based on
        total impulse
        """
        impulse = self.total_impulse
        if impulse <= 2.5:
            return "A"
        elif impulse <= 5.0:
            return "B"
        elif impulse <= 10.0:
            return "C"
        elif impulse <= 20.0:
            return "D"
        elif impulse <= 40.0:
            return "E"
        elif impulse <= 80.0:
            return "F"
        elif impulse <= 160.0:
            return "G"
        elif impulse <= 320.0:
            return "H"
        elif impulse <= 640.0:
            return "I"
        elif impulse <= 1280.0:
            return "J"
        elif impulse <= 2560.0:
            return "K"
        elif impulse <= 5120.0:
            return "L"
        elif impulse <= 10240.0:
            return "M"
        elif impulse <= 20480.0:
            return "N"
        else:
            return "O+"

    @property
    def specific_impulse(self) -> float:
        """Calculate specific impulse (Isp) in seconds"""
        if self.propellant_mass <= 0:
            return 0.0
        # Isp = Total Impulse / (Propellant Mass * g)
        # where g = 9.80665 m/s² (standard gravity)
        return self.total_impulse / (self.propellant_mass * 9.80665)

    def __str__(self) -> str:
        info = (
            f"RASP Motor: {self.designation} by {self.manufacturer}\n"
            f"  Class: {self.impulse_class}\n"
            f"  Diameter: {self.diameter:.0f}mm\n"
            f"  Length: {self.length:.0f}mm\n"
            f"  Propellant Mass: {self.propellant_mass:.3f}kg\n"
            f"  Total Mass: {self.total_mass:.3f}kg\n"
            f"  Total Impulse: {self.total_impulse:.1f}Ns\n"
            f"  Peak Thrust: {self.peak_thrust:.1f}N\n"
            f"  Burn Time: {self.burn_time:.2f}s\n"
            f"  Thrust Points: {len(self.thrust_curve)}"
        )

        if SCIPY_AVAILABLE:
            info += " (scipy-enhanced)"

        return info
