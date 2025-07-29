"""
Core parsing functionality for RASP motor files
"""

from typing import List
from pathlib import Path

from .models import RASPMotor, ThrustCurvePoint
from .exceptions import (
    RASPParseError,
    RASPFileNotFoundError,
    RASPHeaderError,
)


class RASPParser:
    """Parser for RASP format rocket motor files"""

    @staticmethod
    def parse_file(file_path: str) -> RASPMotor:
        """
        Parse a RASP file and return a RASPMotor object

        Args:
            file_path: Path to the .eng file

        Returns:
            RASPMotor object with parsed data

        Raises:
            RASPFileNotFoundError: If the file doesn't exist
            RASPParseError: If the file cannot be parsed
        """
        path = Path(file_path)
        if not path.exists():
            raise RASPFileNotFoundError(f"RASP file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return RASPParser.parse_string(content)
        except Exception as e:
            if isinstance(e, RASPParseError):
                raise
            raise RASPParseError(f"Failed to parse RASP file {file_path}: {str(e)}")

    @staticmethod
    def parse_string(content: str) -> RASPMotor:
        """
        Parse RASP content from a string

        Args:
            content: The RASP file content as a string

        Returns:
            RASPMotor object with parsed data

        Raises:
            RASPParseError: If the content cannot be parsed
        """
        content = content.strip()
        if not content:
            raise RASPParseError("Empty RASP file")

        lines = content.split("\n")

        comments = []
        header_line = None
        thrust_data: List[ThrustCurvePoint] = []

        # Parse lines
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            if line.startswith(";"):
                # Comment line
                comments.append(line[1:].strip())
            elif header_line is None:
                # First non-comment line is the header
                header_line = line
            else:
                # Thrust curve data
                try:
                    parts = line.split()
                    if len(parts) >= 2:
                        time = float(parts[0])
                        thrust = float(parts[1])
                        thrust_data.append(ThrustCurvePoint(time, thrust))
                except ValueError:
                    # Skip invalid lines silently
                    continue

        if header_line is None:
            raise RASPHeaderError("No header line found in RASP file")

        # Parse header line
        motor_data = RASPParser._parse_header(header_line)

        return RASPMotor(**motor_data, thrust_curve=thrust_data, comments=comments)

    @staticmethod
    def _parse_header(header_line: str) -> dict:
        """
        Parse the RASP header line

        Args:
            header_line: The header line to parse

        Returns:
            Dictionary with parsed header data

        Raises:
            RASPHeaderError: If header format is invalid
        """
        header_parts = header_line.split()
        if len(header_parts) < 7:
            raise RASPHeaderError(
                "Invalid header format: expected 7 fields, "
                f"got {len(header_parts)}: {header_line}"
            )

        try:
            return {
                "designation": header_parts[0],
                "diameter": float(header_parts[1]),
                "length": float(header_parts[2]),
                "delays": header_parts[3],
                "propellant_mass": float(header_parts[4]),  # kg
                "total_mass": float(header_parts[5]),  # kg (initial weight)
                "manufacturer": header_parts[6] if len(header_parts) > 6 else "Unknown",
            }
        except (ValueError, IndexError) as e:
            raise RASPHeaderError(
                f"Failed to parse header values: {header_line}"
            ) from e


# Convenience functions
def load_rasp_motor(file_path: str) -> RASPMotor:
    """Load and parse a RASP motor file"""
    return RASPParser.parse_file(file_path)


def load_rasp_motors(directory: str, pattern: str = "*.eng") -> List[RASPMotor]:
    """
    Load all RASP motor files from a directory

    Args:
        directory: Directory to search for RASP files
        pattern: File pattern to match (default: "*.eng")

    Returns:
        List of RASPMotor objects
    """
    motors = []
    path = Path(directory)

    for file_path in path.glob(pattern):
        try:
            motor = load_rasp_motor(str(file_path))
            motors.append(motor)
        except RASPParseError as e:
            print(f"Warning: Failed to load {file_path}: {e}")

    return motors
