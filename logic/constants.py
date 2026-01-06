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
