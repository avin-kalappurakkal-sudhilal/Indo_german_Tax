from logic.constants import TAX_YEAR_CONSTANTS

def estimate_social_security(gross_salary, year, has_kids=True):
    """
    Estimates the employee's share of German social security contributions for a given year.

    Args:
        gross_salary (float): The annual gross salary.
        year (int): The tax year (e.g., 2024, 2025, 2026).
        has_kids (bool): True if the person has children, False otherwise.
                         This affects the nursing insurance rate.

    Returns:
        dict: A dictionary containing the estimated employee contributions for
              pension, unemployment, health, and nursing insurance.
    """
    if year not in TAX_YEAR_CONSTANTS:
        raise ValueError(f"Tax constants for year {year} are not available.")

    year_constants = TAX_YEAR_CONSTANTS[year]
    pension_cap = year_constants['SOCIAL_SECURITY_CAPS']['pension']
    health_cap = year_constants['SOCIAL_SECURITY_CAPS']['health']

    pension = min(gross_salary, pension_cap) * 0.093
    unemployment = min(gross_salary, pension_cap) * 0.013
    # Health insurance: 7.3% base + 1.45% average additional contribution = 8.75%
    health = min(gross_salary, health_cap) * 0.0875
    # Nursing insurance rate is lower for people with children.
    nursing = min(gross_salary, health_cap) * (0.018 if has_kids else 0.024)

    return {
        "pension": pension,
        "unemployment": unemployment,
        "health": health,
        "nursing": nursing,
    }
