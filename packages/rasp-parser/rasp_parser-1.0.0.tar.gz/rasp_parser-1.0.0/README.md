# RASP Parser

[![PyPI version](https://badge.fury.io/py/rasp-parser.svg)](https://badge.fury.io/py/rasp-parser)
[![Python Support](https://img.shields.io/pypi/pyversions/rasp-parser.svg)](https://pypi.org/project/rasp-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/gituser12981u2/rasp-parser/workflows/Tests/badge.svg)](https://github.com/gituser12981u2/rasp-parser/actions)

A Python library for parsing rocket motor data files in RASP format (.eng files). RASP (Rocket Altitude Simulation Program) format is the standard for rocket motor data interchange used by flight simulators like OpenRocket, RockSim, and others.

## Features

- **Parse RASP/ENG files** with full validation
- **High-accuracy integration** using cubic splines (when scipy available) or adaptive Simpson's rule
- **Comprehensive motor data** including thrust curves, performance metrics, and motor specifications
- **Robust error handling** with detailed error messages
- **Type hints** for better IDE support
- **Zero required dependencies** (scipy optional for enhanced accuracy)

## Installation

```bash
# Basic installation
pip install rasp-parser

# With scipy for enhanced accuracy
pip install rasp-parser[scipy]

# Development installation
pip install rasp-parser[dev]
```

## Quick Start

```python
import rasp_parser

# Parse a single motor file
motor = rasp_parser.load_rasp_motor("Estes_D12.eng")

# Display motor information
print(motor)
# Output:
# RASP Motor: D12 by Estes
#   Class: D
#   Diameter: 24mm
#   Length: 70mm
#   Propellant Mass: 0.012kg
#   Total Mass: 0.024kg
#   Total Impulse: 8.8Ns
#   Peak Thrust: 17.3N
#   Burn Time: 1.6s
#   Thrust Points: 15

# Access motor properties
print(f"Motor class: {motor.impulse_class}")
print(f"Total impulse: {motor.total_impulse:.1f} Ns")
print(f"Specific impulse: {motor.specific_impulse:.1f} s")

# Get interpolated thrust at any time
thrust_at_0_5s = motor.get_interpolated_thrust(0.5)
print(f"Thrust at 0.5s: {thrust_at_0_5s:.1f} N")

# Load multiple motors from directory
motors = rasp_parser.load_rasp_motors("motor_database/")
print(f"Loaded {len(motors)} motors")
```

## Motor Data Structure

```python
@dataclass
class RASPMotor:
    designation: str          # Motor designation (e.g., "D12")
    diameter: float          # Diameter in mm
    length: float           # Length in mm  
    delays: str             # Available delays (e.g., "0-3-5-7")
    propellant_mass: float  # Propellant mass in kg
    total_mass: float       # Total motor mass in kg
    manufacturer: str       # Manufacturer name
    thrust_curve: List[ThrustCurvePoint]  # Time/thrust data points
    comments: List[str]     # Comments from file
    
    # Calculated properties
    total_impulse: float    # Integrated total impulse
    peak_thrust: float      # Maximum thrust
    burn_time: float        # Motor burn duration
    average_thrust: float   # Average thrust over burn time
    impulse_class: str      # Motor class (A, B, C, etc.)
    specific_impulse: float # Isp in seconds
```

## Integration Methods

The library automatically selects the best integration method available:

1. **Cubic Spline Integration** (when scipy available)
   - Most accurate for typical thrust curves
   - Handles sparse data well
   - Analytical integration of smooth spline

2. **Adaptive Simpson's Rule** (fallback)
   - High accuracy without dependencies
   - 4th-order accuracy vs 2nd-order trapezoidal

3. **Trapezoidal Rule** (final fallback)
   - For very sparse data (2 points)

```python
# Check which integration method is active
print(f"Integration method: {rasp_parser.get_integration_method()}")
```

## Validation

```python
# Validate motor data
warnings = rasp_parser.validate_motor(motor)
if warnings:
    for warning in warnings:
        print(f"⚠️  {warning}")

# Strict validation (raises exception on issues)
try:
    rasp_parser.validate_motor(motor, strict=True)
    print("✅ Motor validation passed")
except rasp_parser.RASPValidationError as e:
    print(f"❌ Validation failed: {e}")
```

## Advanced Usage

### Custom Parsing

```python
# Parse from string content
with open("motor.eng", "r") as f:
    content = f.read()

motor = rasp_parser.RASPParser.parse_string(content)
```

### Error Handling

```python
try:
    motor = rasp_parser.load_rasp_motor("missing_file.eng")
except rasp_parser.RASPFileNotFoundError:
    print("File not found")
except rasp_parser.RASPHeaderError as e:
    print(f"Invalid header: {e}")
except rasp_parser.RASPThrustCurveError as e:
    print(f"Invalid thrust data: {e}")
```

### Working with Thrust Curves

```python
# Access raw thrust curve data
for point in motor.thrust_curve:
    print(f"t={point.time:.3f}s, F={point.thrust:.1f}N")

# Generate smooth thrust curve using interpolation
import numpy as np
times = np.linspace(0, motor.burn_time, 100)
smooth_thrust = [motor.get_interpolated_thrust(t) for t in times]
```

## RASP File Format

RASP files (.eng) contain rocket motor data in a simple text format:

```RASP
; Comments start with semicolon
; Motor: Estes D12
D12 24 70 0-3-5-7 0.0125 0.0242 Estes
0.000 0.0
0.050 8.0
0.100 15.0
0.200 14.0
...
1.600 0.0

```

**Header format:** `designation diameter length delays propellant_mass total_mass manufacturer`

- **designation**: Motor name (e.g., "D12")
- **diameter**: Motor diameter in mm
- **length**: Motor length in mm
- **delays**: Available ejection delays in seconds
- **propellant_mass**: Propellant mass in kg
- **total_mass**: Total loaded motor mass in kg
- **manufacturer**: Manufacturer code/name

## Requirements

- Python 3.8+
- scipy (optional, for enhanced accuracy)

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file.

## Acknowledgments

- Based on the RASP format originally developed by G. Harry Stine
- Inspired by the rocketry community and flight simulation tools
- Thanks to [ThrustCurve.org](https://www.thrustcurve.org/) for format documentation
