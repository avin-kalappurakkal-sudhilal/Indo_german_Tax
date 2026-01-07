# logic/constants.py
# In a real app, this should be configurable or fetched dynamically.
INR_TO_EUR_RATE = 0.011 

# Tax constants (approximations for recent years)
WERBUNGSKOSTEN_PAUSCHALE = 1230.0
BANK_FEE_FLAT_RATE = 16.0
INTERNET_PHONE_FLAT_RATE = 240.0 
HOME_OFFICE_DAY_RATE = 6.0
MOVING_LUMP_SUM_NON_EU = 890.0

# Deduction rates & limits
KITA_DEDUCTION_RATE = 2/3
NEBENKOSTEN_LABOR_CREDIT_RATE = 0.20
MAX_HOME_OFFICE_DEDUCTION = 1260.0 # Maximum home office deduction per person

# Commuter allowance (Entfernungspauschale)
COMMUTE_ALLOWANCE_LOW_KM = 0.30
COMMUTE_ALLOWANCE_HIGH_KM = 0.38
COMMUTE_ALLOWANCE_THRESHOLD_KM = 20

# Solidarity Surcharge exemption limits (Freigrenze) based on tax liability
SOLI_EXEMPTION_LIMITS = {
    2024: 18130,
    2025: 19450,
    2026: 20350
}

# Constants for different tax years
TAX_YEAR_CONSTANTS = {
    2024: {
        'BASIC_ALLOWANCE': 11784,
        'CHILD_ALLOWANCE': 9312,
        'SOCIAL_SECURITY_CAPS': {
            # Note: Using West Germany cap. East Germany is €89,400.
            # Unified from 2025.
            'pension': 90600,
            'health': 62100,
        },
        'ADDITIONAL_HEALTH_INSURANCE_RATE': 0.017,
    },
    2025: {
        'BASIC_ALLOWANCE': 12096,
        'CHILD_ALLOWANCE': 9600,
        'SOCIAL_SECURITY_CAPS': {
            'pension': 96600,
            'health': 66150,
        },
        'ADDITIONAL_HEALTH_INSURANCE_RATE': 0.025,
    },
    2026: {
        'BASIC_ALLOWANCE': 12348,
        'CHILD_ALLOWANCE': 9756,
        'SOCIAL_SECURITY_CAPS': {
            'pension': 101400,
            'health': 69750, # Based on previous version of estimate_social_security_2026
        },
        'ADDITIONAL_HEALTH_INSURANCE_RATE': 0.029,
    }
}
