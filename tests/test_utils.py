# tests/test_utils.py
from logic.utils import estimate_social_security
import sys

def test_estimate_social_security_2024():
    print("Running test_estimate_social_security_2024")
    # Test with a salary below all caps, no children
    result = estimate_social_security(50000, 2024, num_children=0)
    assert abs(result['pension'] - 50000 * 0.093) < 0.01
    assert abs(result['unemployment'] - 50000 * 0.013) < 0.01
    assert abs(result['health'] - 50000 * (0.073 + 0.017 / 2)) < 0.01
    assert abs(result['nursing'] - 50000 * 0.023) < 0.01

    # Test with a salary above all caps, 1 child
    result_high = estimate_social_security(100000, 2024, num_children=1)
    assert abs(result_high['pension'] - 90600 * 0.093) < 0.01
    assert abs(result_high['unemployment'] - 90600 * 0.013) < 0.01
    assert abs(result_high['health'] - 62100 * (0.073 + 0.017 / 2)) < 0.01
    assert abs(result_high['nursing'] - 62100 * 0.017) < 0.01
    print("test_estimate_social_security_2024 passed")

def test_estimate_social_security_2025():
    print("Running test_estimate_social_security_2025")
    # Test with a salary below all caps, no children
    result = estimate_social_security(60000, 2025, num_children=0)
    assert abs(result['pension'] - 60000 * 0.093) < 0.01
    assert abs(result['unemployment'] - 60000 * 0.013) < 0.01
    assert abs(result['health'] - 60000 * (0.073 + 0.025 / 2)) < 0.01
    assert abs(result['nursing'] - 60000 * 0.023) < 0.01
    
    # Test with a salary above all caps, no children
    result_high = estimate_social_security(110000, 2025, num_children=0)
    assert abs(result_high['pension'] - 96600 * 0.093) < 0.01
    assert abs(result_high['unemployment'] - 96600 * 0.013) < 0.01
    assert abs(result_high['health'] - 66150 * (0.073 + 0.025 / 2)) < 0.01
    assert abs(result_high['nursing'] - 66150 * 0.023) < 0.01
    print("test_estimate_social_security_2025 passed")

def test_estimate_social_security_2026():
    print("Running test_estimate_social_security_2026")
    # Test with a salary below all caps, 2 children
    result = estimate_social_security(70000, 2026, num_children=2)
    assert abs(result['pension'] - 70000 * 0.093) < 0.01
    assert abs(result['unemployment'] - 70000 * 0.013) < 0.01
    assert abs(result['health'] - 70000 * (0.073 + 0.029 / 2)) < 0.01
    assert abs(result['nursing'] - 70000 * (0.017 - 0.0025)) < 0.01

    # Test with a salary above all caps, 2 children
    result_high = estimate_social_security(120000, 2026, num_children=2)
    assert abs(result_high['pension'] - 101400 * 0.093) < 0.01
    assert abs(result_high['unemployment'] - 101400 * 0.013) < 0.01
    assert abs(result_high['health'] - 69750 * (0.073 + 0.029 / 2)) < 0.01
    assert abs(result_high['nursing'] - 69750 * (0.017 - 0.0025)) < 0.01
    print("test_estimate_social_security_2026 passed")

def test_nursing_insurance_by_children():
    print("Running test_nursing_insurance_by_children")
    salary = 50000
    year = 2024
    health_cap = TAX_YEAR_CONSTANTS[year]['SOCIAL_SECURITY_CAPS']['health']
    
    # 0 children: 2.3%
    res0 = estimate_social_security(salary, year, num_children=0)
    assert abs(res0['nursing'] - min(salary, health_cap) * 0.023) < 0.01

    # 1 child: 1.7%
    res1 = estimate_social_security(salary, year, num_children=1)
    assert abs(res1['nursing'] - min(salary, health_cap) * 0.017) < 0.01

    # 2 children: 1.7% - 0.25% = 1.45%
    res2 = estimate_social_security(salary, year, num_children=2)
    assert abs(res2['nursing'] - min(salary, health_cap) * (0.017 - 0.0025)) < 0.01
    
    # 3 children: 1.7% - 0.5% = 1.2%
    res3 = estimate_social_security(salary, year, num_children=3)
    assert abs(res3['nursing'] - min(salary, health_cap) * (0.017 - 0.0050)) < 0.01

    # 4 children: 1.7% - 0.75% = 0.95%
    res4 = estimate_social_security(salary, year, num_children=4)
    assert abs(res4['nursing'] - min(salary, health_cap) * (0.017 - 0.0075)) < 0.01

    # 5 children: 1.7% - 1.0% = 0.7%
    res5 = estimate_social_security(salary, year, num_children=5)
    assert abs(res5['nursing'] - min(salary, health_cap) * (0.017 - 0.0100)) < 0.01

    # 6 children: capped at 5 children level
    res6 = estimate_social_security(salary, year, num_children=6)
    assert abs(res6['nursing'] - min(salary, health_cap) * (0.017 - 0.0100)) < 0.01
    print("test_nursing_insurance_by_children passed")

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
    from logic.constants import TAX_YEAR_CONSTANTS
    test_estimate_social_security_2024()
    test_estimate_social_security_2025()
    test_estimate_social_security_2026()
    test_nursing_insurance_by_children()
    test_invalid_year()
    print("All tests passed!")
