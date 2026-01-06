# logic/tax_calculator.py

def calculate_german_tax(zvE, is_married=True):
    """
    Calculates German income tax based on the official formula (approximated for recent years).
    
    Args:
        zvE (float): The taxable income (zu versteuerndes Einkommen).
        is_married (bool): True if filing jointly, which triggers the 'Splitting' method.
        
    Returns:
        float: The calculated income tax amount.
    """
    # For married couples (Splittingverfahren), we halve the income, 
    # calculate tax, then double the result.
    if is_married:
        zvE = zvE / 2

    tax = 0
    if zvE <= 11604:
        tax = 0
    elif zvE <= 17005:
        y = (zvE - 11604) / 10000
        tax = (922.98 * y + 1400) * y
    elif zvE <= 66760:
        z = (zvE - 17005) / 10000
        tax = (181.19 * z + 2397) * z + 1025.38
    elif zvE <= 277825:
        tax = 0.42 * zvE - 10602.13
    else:
        tax = 0.45 * zvE - 18936.88

    return (tax * 2) if is_married else tax