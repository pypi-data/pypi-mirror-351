"""
Tests for core parsing functionality
"""

import pytest
from rasp_parser.core import RASPParser
from rasp_parser.exceptions import (
    RASPFileNotFoundError,
    RASPHeaderError,
    RASPParseError,
)


class TestRASPParser:
    """Test RASP file parsing"""

    def test_parse_valid_motor(self):
        """Test parsing a valid RASP motor"""
        rasp_content = """
; Test motor
; Comments here
D12 24 70 0-3-5 0.0125 0.0242 Estes
0.000 0.0
0.050 8.0
0.100 15.0
0.200 14.0
1.600 0.0
"""
        motor = RASPParser.parse_string(rasp_content)

        assert motor.designation == "D12"
        assert motor.diameter == 24
        assert motor.length == 70
        assert motor.delays == "0-3-5"
        assert motor.propellant_mass == 0.0125
        assert motor.total_mass == 0.0242
        assert motor.manufacturer == "Estes"
        assert len(motor.thrust_curve) == 5
        assert len(motor.comments) == 2

    def test_parse_minimal_motor(self):
        """Test parsing with minimal required fields"""
        rasp_content = "D12 24 70 0 0.0125 0.0242 Estes\n0.0 0.0\n1.0 0.0"
        motor = RASPParser.parse_string(rasp_content)

        assert motor.designation == "D12"
        assert len(motor.thrust_curve) == 2

    def test_parse_empty_content(self):
        """Test parsing empty content raises error"""
        with pytest.raises(RASPParseError, match="Empty RASP file"):
            RASPParser.parse_string("")

    def test_parse_no_header(self):
        """Test parsing with no header raises error"""
        rasp_content = "; Just comments\n; More comments"
        with pytest.raises(RASPHeaderError, match="No header line found"):
            RASPParser.parse_string(rasp_content)

    def test_parse_invalid_header_fields(self):
        """Test parsing with insufficient header fields"""
        rasp_content = "D12 24 70"  # Only 3 fields, need 7
        with pytest.raises(RASPHeaderError, match="expected 7 fields"):
            RASPParser.parse_string(rasp_content)

    def test_parse_invalid_header_values(self):
        """Test parsing with invalid numeric values in header"""
        rasp_content = "D12 abc 70 0 0.0125 0.0242 Estes"
        with pytest.raises(RASPHeaderError, match="Failed to parse header values"):
            RASPParser.parse_string(rasp_content)

    def test_parse_file_not_found(self):
        """Test parsing non-existent file raises error"""
        with pytest.raises(RASPFileNotFoundError):
            RASPParser.parse_file("nonexistent.eng")

    def test_parse_with_comments_and_blanks(self):
        """Test parsing handles comments and blank lines properly"""
        rasp_content = """
; First comment

; Second comment
D12 24 70 0 0.0125 0.0242 Estes

0.0 0.0
; Mid comment
1.0 5.0

2.0 0.0
"""
        motor = RASPParser.parse_string(rasp_content)

        assert len(motor.comments) == 3
        assert motor.comments[0] == "First comment"
        assert motor.comments[1] == "Second comment"
        assert len(motor.thrust_curve) == 3

    def test_parse_invalid_thrust_data(self):
        """Test parsing with invalid thrust curve data"""
        rasp_content = """
D12 24 70 0 0.0125 0.0242 Estes
0.0 0.0
invalid data
1.0 0.0
"""
        # Should skip invalid line and continue
        motor = RASPParser.parse_string(rasp_content)
        assert len(motor.thrust_curve) == 2

    def test_parse_extra_header_fields(self):
        """Test parsing with extra header fields (should work)"""
        rasp_content = "D12 24 70 0 0.0125 0.0242 Estes ExtraField\n0.0 0.0" "\n1.0 0.0"
        motor = RASPParser.parse_string(rasp_content)

        assert motor.manufacturer == "Estes"  # Should still parse correctly

    def test_motor_properties(self):
        """Test calculated motor properties"""
        rasp_content = """
D12 24 70 0 0.0125 0.0242 Estes
0.0 0.0
0.5 10.0
1.0 20.0
1.5 10.0
2.0 0.0
"""
        motor = RASPParser.parse_string(rasp_content)

        assert motor.burn_time == 2.0
        assert motor.peak_thrust == 20.0
        assert motor.total_impulse > 0
        assert motor.average_thrust > 0
        assert motor.impulse_class in "ABCDEFGHIJKLMNO+"
        assert motor.specific_impulse > 0
