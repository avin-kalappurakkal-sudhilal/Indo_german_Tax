# logic/tax_calculator.py
from .constants import TAX_YEAR_CONSTANTS

def calculate_german_tax(zvE, year, is_married=True):
    """
    Calculates German income tax based on the official formula (approximated for recent years).
    
    Args:
        zvE (float): The taxable income (zu versteuerndes Einkommen).
        year (int): The tax year to use for constants.
        is_married (bool): True if filing jointly, which triggers the 'Splitting' method.
        
    Returns:
        float: The calculated income tax amount.
    """
    if year not in TAX_YEAR_CONSTANTS:
        raise ValueError(f"Tax constants for year {year} are not available.")

    basic_allowance = TAX_YEAR_CONSTANTS[year]['BASIC_ALLOWANCE']

    # For married couples (Splittingverfahren), we halve the income, 
    # calculate tax, then double the result.
    if is_married:
        zvE = zvE / 2
        # The basic allowance is also halved for the formula
        basic_allowance = basic_allowance / 2

    # NOTE: The tax brackets below are a rough approximation based on 2023/2024 values.
    # A real-world application would need to update these for each year.
    # The primary change for this function is using the dynamic basic_allowance.
    tax = 0
    if zvE <= basic_allowance:
        tax = 0
    elif zvE <= 17005: # This threshold is for 2024
        y = (zvE - basic_allowance) / 10000
        tax = (922.98 * y + 1400) * y
    elif zvE <= 66760: # This threshold is for 2024
        # The formula needs to be adjusted based on the prior bracket's calculation
        # For simplicity, we'll keep the old formula but acknowledge it's an approximation
        z = (zvE - 17005) / 10000
        tax = (181.19 * z + 2397) * z + 1025.38
    elif zvE <= 277825:
        tax = 0.42 * zvE - 10602.13
    else:
        tax = 0.45 * zvE - 18936.88

    return (tax * 2) if is_married else tax