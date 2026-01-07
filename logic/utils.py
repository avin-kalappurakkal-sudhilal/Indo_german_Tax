def estimate_social_security_2026(gross_salary, has_kids=True):
    """
    Estimates the employee's share of German social security contributions for 2026.

    Args:
        gross_salary (float): The annual gross salary.
        has_kids (bool): True if the person has children, False otherwise.
                         This affects the nursing insurance rate.

    Returns:
        dict: A dictionary containing the estimated employee contributions for
              pension, unemployment, health, and nursing insurance.
    """
    pension = min(gross_salary, 101400) * 0.093
    unemployment = min(gross_salary, 101400) * 0.013
    # Health insurance: 7.3% base + 1.45% average additional contribution = 8.75%
    health = min(gross_salary, 69750) * 0.0875
    # Nursing insurance rate is lower for people with children.
    nursing = min(gross_salary, 69750) * (0.018 if has_kids else 0.024)

    return {
        "pension": pension,
        "unemployment": unemployment,
        "health": health,
        "nursing": nursing,
    }
