# tests/test_utils.py
from logic.utils import estimate_social_security
import sys

def test_estimate_social_security_2024():
    print("Running test_estimate_social_security_2024")
    # Test with a salary below all caps
    result = estimate_social_security(50000, 2024)
    assert result['pension'] == 50000 * 0.093
    assert result['unemployment'] == 50000 * 0.013
    assert result['health'] == 50000 * 0.0875
    assert result['nursing'] == 50000 * 0.018

    # Test with a salary above all caps
    result_high = estimate_social_security(100000, 2024)
    assert result_high['pension'] == 90600 * 0.093
    assert result_high['unemployment'] == 90600 * 0.013
    assert result_high['health'] == 62100 * 0.0875
    assert result_high['nursing'] == 62100 * 0.018
    print("test_estimate_social_security_2024 passed")

def test_estimate_social_security_2025():
    print("Running test_estimate_social_security_2025")
    # Test with a salary below all caps
    result = estimate_social_security(60000, 2025)
    assert result['pension'] == 60000 * 0.093
    assert result['unemployment'] == 60000 * 0.013
    assert result['health'] == 60000 * 0.0875
    assert result['nursing'] == 60000 * 0.018
    
    # Test with a salary above all caps
    result_high = estimate_social_security(110000, 2025, has_kids=False)
    assert result_high['pension'] == 96600 * 0.093
    assert result_high['unemployment'] == 96600 * 0.013
    assert result_high['health'] == 66150 * 0.0875
    assert result_high['nursing'] == 66150 * 0.024
    print("test_estimate_social_security_2025 passed")

def test_estimate_social_security_2026():
    print("Running test_estimate_social_security_2026")
    # Test with a salary below all caps
    result = estimate_social_security(70000, 2026)
    assert result['pension'] == 70000 * 0.093
    assert result['unemployment'] == 70000 * 0.013
    assert result['health'] == 70000 * 0.0875
    assert result['nursing'] == 70000 * 0.018

    # Test with a salary above all caps
    result_high = estimate_social_security(120000, 2026)
    assert result_high['pension'] == 101400 * 0.093
    assert result_high['unemployment'] == 101400 * 0.013
    assert result_high['health'] == 69750 * 0.0875
    assert result_high['nursing'] == 69750 * 0.018
    print("test_estimate_social_security_2026 passed")

def test_invalid_year():
    print("Running test_invalid_year")
    try:
        estimate_social_security(50000, 2023)
        # If it doesn't raise an error, fail the test
        print("test_invalid_year failed: ValueError not raised")
        sys.exit(1)
    except ValueError as e:
        assert str(e) == "Tax constants for year 2023 are not available."
        print("test_invalid_year passed")

if __name__ == "__main__":
    test_estimate_social_security_2024()
    test_estimate_social_security_2025()
    test_estimate_social_security_2026()
    test_invalid_year()
    print("All tests passed!")