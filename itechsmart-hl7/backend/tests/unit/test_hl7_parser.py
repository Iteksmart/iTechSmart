"""
Unit tests for HL7 parser
"""
import pytest
from app.core.hl7_parser import HL7Parser


def test_parse_hl7_message(sample_hl7_message):
    """Test parsing HL7 v2.x message"""
    parser = HL7Parser()
    result = parser.parse(sample_hl7_message)
    
    assert result is not None
    assert "MSH" in result
    assert "PID" in result
    assert result["PID"]["patient_name"] == "DOE^JOHN^A"


def test_parse_invalid_hl7():
    """Test parsing invalid HL7 message"""
    parser = HL7Parser()
    
    with pytest.raises(Exception):
        parser.parse("INVALID MESSAGE")


def test_extract_patient_info(sample_hl7_message):
    """Test extracting patient information"""
    parser = HL7Parser()
    result = parser.parse(sample_hl7_message)
    patient = parser.extract_patient_info(result)
    
    assert patient["mrn"] == "123456"
    assert patient["name"] == "DOE^JOHN^A"
    assert patient["dob"] == "19800101"
    assert patient["gender"] == "M"