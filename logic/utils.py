from logic.constants import TAX_YEAR_CONSTANTS

def estimate_social_security(gross_salary, year, num_children=0):
    """
    Estimates the employee's share of German social security contributions for a given year.

    Args:
        gross_salary (float): The annual gross salary.
        year (int): The tax year (e.g., 2024, 2025, 2026).
        num_children (int): The number of children. This affects the nursing insurance rate.

    Returns:
        dict: A dictionary containing the estimated employee contributions for
              pension, unemployment, health, and nursing insurance.
    """
    if year not in TAX_YEAR_CONSTANTS:
        raise ValueError(f"Tax constants for year {year} are not available.")

    year_constants = TAX_YEAR_CONSTANTS[year]
    pension_cap = year_constants['SOCIAL_SECURITY_CAPS']['pension']
    health_cap = year_constants['SOCIAL_SECURITY_CAPS']['health']
    additional_health_rate = year_constants['ADDITIONAL_HEALTH_INSURANCE_RATE']

    pension = min(gross_salary, pension_cap) * 0.093
    unemployment = min(gross_salary, pension_cap) * 0.013
    
    # Health insurance: 7.3% base + half of the additional contribution rate
    health_insurance_rate = 0.073 + (additional_health_rate / 2)
    health = min(gross_salary, health_cap) * health_insurance_rate

    # Nursing insurance (Pflegeversicherung)
    # Base rate: 3.4% (employee share 1.7%).
    # Childless people (over 23) pay a 0.6% surcharge.
    # For people with children, the rate is reduced for the 2nd to 5th child.
    if num_children == 0:
        # 1.7% base + 0.6% surcharge for childless employees
        nursing_rate = 0.023
    else:
        # Reduction of 0.25 percentage points from the employee's share for each child from the 2nd to the 5th.
        # Max reduction is for 4 children (2nd, 3rd, 4th, 5th).
        reduction_count = min(max(0, num_children - 1), 4)
        reduction = reduction_count * 0.0025
        # 1.7% base - reduction
        nursing_rate = 0.017 - reduction
    
    nursing = min(gross_salary, health_cap) * nursing_rate

    return {
        "pension": pension,
        "unemployment": unemployment,
        "health": health,
        "nursing": nursing,
    }
