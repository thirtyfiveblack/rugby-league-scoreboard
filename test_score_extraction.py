"""
Unit tests for score extraction and formatting functions.

Tests various score formats to ensure proper extraction:
- Dict objects
- Stringified dicts (JSON)
- Numeric strings
- Integers and floats
- Edge cases
"""

import json
import re
import unittest
from unittest.mock import Mock


def extract_score_mock(team_data, logger):
    """
    Mock version of extract_score function from sports.py
    Tests the same logic without requiring the full class structure.
    """
    score = team_data.get("score")
    if score is None:
        return "0"
    
    # If score is a dict (e.g., {"value": 75}), extract the value
    if isinstance(score, dict):
        score_value = score.get("value", 0)
        # Also check for other possible keys
        if score_value == 0:
            score_value = score.get("displayValue", score.get("score", 0))
    else:
        score_value = score
    
    # Convert to integer to remove decimal points, then to string
    try:
        # Handle string scores - check if it's a string representation of a dict first
        if isinstance(score_value, str):
            # Remove any whitespace
            score_value = score_value.strip()
            
            # Check if it's a JSON string (starts with { or [)
            if score_value.startswith(('{', '[')):
                try:
                    # Try to parse as JSON
                    parsed = json.loads(score_value)
                    if isinstance(parsed, dict):
                        score_value = parsed.get("value", parsed.get("displayValue", parsed.get("score", 0)))
                    elif isinstance(parsed, list) and len(parsed) > 0:
                        score_value = parsed[0]
                    else:
                        score_value = parsed
                except (json.JSONDecodeError, ValueError):
                    # If JSON parsing fails, try to extract number from string
                    numbers = re.findall(r'\d+', score_value)
                    if numbers:
                        score_value = float(numbers[0])
                    else:
                        logger.warning(f"Could not extract score from JSON-like string: {score_value}")
                        return "0"
            else:
                # Try to parse as float/int first
                try:
                    score_value = float(score_value)
                except ValueError:
                    # If it's not a number, try to extract number from string
                    numbers = re.findall(r'\d+', score_value)
                    if numbers:
                        score_value = float(numbers[0])
                    else:
                        logger.warning(f"Could not extract score from string: {score_value}")
                        return "0"
        # Convert to int to remove decimals, then to string
        return str(int(float(score_value)))
    except (ValueError, TypeError) as e:
        logger.warning(f"Error extracting score: {e}, score type: {type(score)}, score value: {score}")
        return "0"


def format_score_mock(score, logger):
    """
    Mock version of format_score function from basketball.py and sports.py
    Tests the same logic without requiring the full class structure.
    """
    try:
        # Handle None or empty values
        if score is None:
            return "0"
        
        # If it's already a string, try to parse it
        if isinstance(score, str):
            # Remove any whitespace
            score = score.strip()
            # If empty, return 0
            if not score:
                return "0"
            
            # Check if it's a JSON string (starts with { or [)
            if score.startswith(('{', '[')):
                try:
                    # Try to parse as JSON
                    parsed = json.loads(score)
                    if isinstance(parsed, dict):
                        score_value = parsed.get("value", parsed.get("displayValue", parsed.get("score", 0)))
                    elif isinstance(parsed, list) and len(parsed) > 0:
                        score_value = parsed[0]
                    else:
                        score_value = parsed
                    return str(int(float(score_value)))
                except (json.JSONDecodeError, ValueError):
                    # If JSON parsing fails, try to extract number from string
                    numbers = re.findall(r'\d+', score)
                    if numbers:
                        return str(int(numbers[0]))
                    logger.warning(f"Could not parse JSON score string: {score}")
                    return "0"
            
            # Try to extract number from string
            try:
                return str(int(float(score)))
            except ValueError:
                # Try to extract first number from string
                numbers = re.findall(r'\d+', score)
                if numbers:
                    return str(int(numbers[0]))
                logger.warning(f"Could not parse score string: {score}")
                return "0"
        
        # Handle dict (shouldn't happen if extraction worked, but be safe)
        if isinstance(score, dict):
            score_value = score.get("value", score.get("displayValue", 0))
            return str(int(float(score_value)))
        
        # Handle numeric types
        return str(int(float(score)))
    except (ValueError, TypeError) as e:
        logger.warning(f"Error formatting score: {e}, score type: {type(score)}, score value: {score}")
        return "0"


class TestScoreExtraction(unittest.TestCase):
    """Test cases for score extraction from team data."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = Mock()
        self.logger.warning = Mock()
        self.logger.debug = Mock()
    
    def test_dict_score_with_value(self):
        """Test extracting score from dict with 'value' key."""
        team_data = {"score": {"value": 75}}
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "75")
    
    def test_dict_score_with_displayValue(self):
        """Test extracting score from dict with 'displayValue' key."""
        team_data = {"score": {"displayValue": "82"}}
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "82")
    
    def test_stringified_dict_json(self):
        """Test extracting score from JSON stringified dict."""
        team_data = {"score": '{"value": 75}'}
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "75")
    
    def test_stringified_dict_single_quotes(self):
        """Test extracting score from single-quoted stringified dict (Python repr format)."""
        # This simulates what might happen if a dict gets stringified incorrectly
        team_data = {"score": "{'value': 75}"}
        # Note: json.loads won't work with single quotes, so it should fall back to regex
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "75")  # Should extract via regex
    
    def test_numeric_string(self):
        """Test extracting score from numeric string."""
        team_data = {"score": "75"}
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "75")
    
    def test_integer_score(self):
        """Test extracting score from integer."""
        team_data = {"score": 75}
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "75")
    
    def test_float_score(self):
        """Test extracting score from float."""
        team_data = {"score": 75.0}
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "75")
    
    def test_float_string_score(self):
        """Test extracting score from float string."""
        team_data = {"score": "75.5"}
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "75")  # Should truncate to int
    
    def test_none_score(self):
        """Test handling None score."""
        team_data = {"score": None}
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "0")
    
    def test_missing_score(self):
        """Test handling missing score key."""
        team_data = {}
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "0")
    
    def test_zero_score(self):
        """Test handling zero score."""
        team_data = {"score": 0}
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "0")
    
    def test_complex_string_with_number(self):
        """Test extracting number from complex string."""
        team_data = {"score": "Score: 75 points"}
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "75")
    
    def test_json_list_format(self):
        """Test extracting score from JSON list format."""
        team_data = {"score": "[75]"}
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "75")
    
    def test_dict_with_nested_structure(self):
        """Test extracting score from dict with nested structure."""
        team_data = {"score": {"value": 75, "displayValue": "75"}}
        result = extract_score_mock(team_data, self.logger)
        self.assertEqual(result, "75")


class TestScoreFormatting(unittest.TestCase):
    """Test cases for score formatting in display methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = Mock()
        self.logger.warning = Mock()
    
    def test_format_dict_score(self):
        """Test formatting dict score."""
        result = format_score_mock({"value": 75}, self.logger)
        self.assertEqual(result, "75")
    
    def test_format_stringified_dict_json(self):
        """Test formatting JSON stringified dict."""
        result = format_score_mock('{"value": 75}', self.logger)
        self.assertEqual(result, "75")
    
    def test_format_stringified_dict_single_quotes(self):
        """Test formatting single-quoted stringified dict."""
        result = format_score_mock("{'value': 75}", self.logger)
        self.assertEqual(result, "75")  # Should extract via regex
    
    def test_format_numeric_string(self):
        """Test formatting numeric string."""
        result = format_score_mock("75", self.logger)
        self.assertEqual(result, "75")
    
    def test_format_integer(self):
        """Test formatting integer."""
        result = format_score_mock(75, self.logger)
        self.assertEqual(result, "75")
    
    def test_format_float(self):
        """Test formatting float."""
        result = format_score_mock(75.5, self.logger)
        self.assertEqual(result, "75")
    
    def test_format_none(self):
        """Test formatting None."""
        result = format_score_mock(None, self.logger)
        self.assertEqual(result, "0")
    
    def test_format_empty_string(self):
        """Test formatting empty string."""
        result = format_score_mock("", self.logger)
        self.assertEqual(result, "0")
    
    def test_format_whitespace_string(self):
        """Test formatting whitespace-only string."""
        result = format_score_mock("   ", self.logger)
        self.assertEqual(result, "0")
    
    def test_format_complex_string(self):
        """Test formatting complex string with number."""
        result = format_score_mock("Score: 75", self.logger)
        self.assertEqual(result, "75")
    
    def test_format_json_list(self):
        """Test formatting JSON list."""
        result = format_score_mock("[75]", self.logger)
        self.assertEqual(result, "75")
    
    def test_format_zero(self):
        """Test formatting zero."""
        result = format_score_mock(0, self.logger)
        self.assertEqual(result, "0")
    
    def test_format_large_number(self):
        """Test formatting large number."""
        result = format_score_mock(12345, self.logger)
        self.assertEqual(result, "12345")


if __name__ == '__main__':
    unittest.main()

