# logic/report_generator.py
from . import constants
from .tax_calculator import calculate_german_tax

DEBUG = True

def d_print(message):
    """A helper function for printing debug messages if DEBUG is True."""
    if DEBUG:
        print(message)

# Helper function for werbungskosten calculation for a single person
def _calculate_single_werbungskosten(ho_days, commute_km, office_days):
    ho = min(ho_days * constants.HOME_OFFICE_DAY_RATE, constants.MAX_HOME_OFFICE_DEDUCTION)
    
    commute = 0.0
    if commute_km > 0 and office_days > 0: # Only calculate if there's actual commute
        if commute_km <= constants.COMMUTE_ALLOWANCE_THRESHOLD_KM:
            commute = commute_km * constants.COMMUTE_ALLOWANCE_LOW_KM * office_days
        else:
            low_km_deduction = constants.COMMUTE_ALLOWANCE_THRESHOLD_KM * constants.COMMUTE_ALLOWANCE_LOW_KM * office_days
            high_km_deduction = (commute_km - constants.COMMUTE_ALLOWANCE_THRESHOLD_KM) * constants.COMMUTE_ALLOWANCE_HIGH_KM * office_days
            commute = low_km_deduction + high_km_deduction
    
    wk = max(constants.WERBUNGSKOSTEN_PAUSCHALE, ho + commute)
    return ho, commute, wk

def _calculate_deductions(data, is_married, de_gross_a, de_gross_b):
    """Calculates all tax-deductible expenses for one or two persons."""
    
    results = {f: 0.0 for f in [
        "ho_a", "commute_a", "wk_a", "pauschale_a_applied",
        "ho_b", "commute_b", "wk_b", "pauschale_b_applied", "total_wk",
        "vorsorge_a", "vorsorge_b", "total_vorsorge",
        "bank_fee_a", "bank_fee_b", "internet_a", "internet_b", "total_flat_rates",
        "other_deductions", "total_deductions"
    ]}
    results["pauschale_a_applied"] = False
    results["pauschale_b_applied"] = False

    # 1. Social Security Contributions (Vorsorgeaufwendungen)
    # These are subtracted from gross income before the tax formula is applied.
    # Person A
    pension_a = data.get("de_pension_a", 0.0)
    health_a = data.get("de_health_a", 0.0)
    nursing_a = data.get("de_nursing_a", 0.0)
    unemployment_a = data.get("de_unemployment_a", 0.0)
    results["vorsorge_a"] = pension_a + health_a + nursing_a + unemployment_a
    # Person B
    pension_b = data.get("de_pension_b", 0.0)
    health_b = data.get("de_health_b", 0.0)
    nursing_b = data.get("de_nursing_b", 0.0)
    unemployment_b = data.get("de_unemployment_b", 0.0)
    results["vorsorge_b"] = pension_b + health_b + nursing_b + unemployment_b
    
    results["total_vorsorge"] = results["vorsorge_a"] + results["vorsorge_b"]

    # 2. Income-Related Expenses (Werbungskosten)
    # Person A
    if de_gross_a > 0:
        ho_a, commute_a, wk_a_raw = _calculate_single_werbungskosten(
            data.get("ho_days_a", 0.0), data.get("commute_km_a", 0.0), data.get("office_days_a", 0.0)
        )
        results["ho_a"], results["commute_a"] = ho_a, commute_a
        if wk_a_raw < constants.WERBUNGSKOSTEN_PAUSCHALE:
            results["wk_a"] = constants.WERBUNGSKOSTEN_PAUSCHALE
            results["pauschale_a_applied"] = True
        else:
            results["wk_a"] = wk_a_raw
    
    # Person B (only if married and has income)
    if is_married and de_gross_b > 0:
        ho_b, commute_b, wk_b_raw = _calculate_single_werbungskosten(
            data.get("ho_days_b", 0.0), data.get("commute_km_b", 0.0), data.get("office_days_b", 0.0)
        )
        results["ho_b"], results["commute_b"] = ho_b, commute_b
        if wk_b_raw < constants.WERBUNGSKOSTEN_PAUSCHALE:
            results["wk_b"] = constants.WERBUNGSKOSTEN_PAUSCHALE
            results["pauschale_b_applied"] = True
        else:
            results["wk_b"] = wk_b_raw
            
    results["total_wk"] = results["wk_a"] + results["wk_b"]

    # 3. Flat-Rate Deductions (often part of Werbungskosten or Sonderausgaben)
    if data.get("bank_fee_a") and de_gross_a > 0:
        results["bank_fee_a"] = constants.BANK_FEE_FLAT_RATE
    if is_married and data.get("bank_fee_b") and de_gross_b > 0:
        results["bank_fee_b"] = constants.BANK_FEE_FLAT_RATE
        
    results["internet_a"] = data.get("internet_a", 0.0) if de_gross_a > 0 else 0.0
    results["internet_b"] = data.get("internet_b", 0.0) if is_married and de_gross_b > 0 else 0.0
    
    # These are typically added to the Werbungskosten pool
    # We will adjust wk_a and wk_b to include these if they don't use the Pauschale
    if not results["pauschale_a_applied"]:
        results["wk_a"] += results["bank_fee_a"] + results["internet_a"]
    if not results["pauschale_b_applied"]:
        results["wk_b"] += results["bank_fee_b"] + results["internet_b"]
    
    results["total_wk"] = results["wk_a"] + results["wk_b"]

    # 4. Other Deductions (Sonderausgaben, außergewöhnliche Belastungen)
    kita_deduction = (data.get("kita_costs", 0.0)) * constants.KITA_DEDUCTION_RATE
    parents_support_deduction = data.get("parents_support", 0.0)
    results["other_deductions"] = kita_deduction + parents_support_deduction
    
    # 5. Grand Total of all deductions to be subtracted from gross
    results["total_deductions"] = results["total_vorsorge"] + results["total_wk"] + results["other_deductions"]
    
    return results

def _calculate_credits(data):
    """Calculates non-refundable tax credits."""
    nk_credit = (data.get("nk_labor") or 0.0) * constants.NEBENKOSTEN_LABOR_CREDIT_RATE
    tds_credit_eur = (data.get("in_tds_inr") or 0.0) * constants.INR_TO_EUR_RATE
    return {
        "nebenkosten_credit": nk_credit,
        "tds_credit": tds_credit_eur,
        "total_credits": nk_credit + tds_credit_eur
    }

def generate_full_report(data):
    """
    Orchestrates the full tax calculation process for a dual-income household 
    and returns a structured report.
    """
    d_print("\n--- REPORT GENERATOR: RAW INPUT DATA ---")
    for key, value in data.items():
        d_print(f"  - {key}: {value}")
    d_print("------------------------------------------")

    # 1. Collect Basic Inputs
    de_gross_a = data.get("de_gross_a", 0.0)
    de_tax_paid_a = data.get("de_tax_paid_a", 0.0)
    de_gross_b = data.get("de_gross_b", 0.0)
    de_tax_paid_b = data.get("de_tax_paid_b", 0.0)
    
    total_gross = de_gross_a + de_gross_b
    total_tax_paid = de_tax_paid_a + de_tax_paid_b
    
    # Determine marital status and correct tax class number from UI data
    is_married = data.get("is_married", False)
    tax_class_index = data.get("tax_class", 0)
    tax_class = 0
    if is_married:
        # Married: Index 0 -> Class 3, 1 -> 4, 2 -> 5
        tax_class = tax_class_index + 3
    else:
        # Single: Index 0 -> Class 1
        tax_class = 1
    
    d_print(f"  - Determined marital status: {is_married} | Tax Class: {tax_class}")

    # 2. Foreign Income (converted to EUR)
    in_rent_eur = data.get("in_rent", 0.0) * constants.INR_TO_EUR_RATE
    in_interest_eur = data.get("in_interest", 0.0) * constants.INR_TO_EUR_RATE
    foreign_income = in_rent_eur + in_interest_eur
    
    # 3. Deductions and Credits
    deductions = _calculate_deductions(data, is_married, de_gross_a, de_gross_b)
    credits = _calculate_credits(data)

    # 4. Taxable Income (zu versteuerndes Einkommen - zvE)
    # This is the final income figure upon which tax is calculated.
    taxable_income_de = total_gross - deductions["total_deductions"]
    taxable_income_de = max(0, taxable_income_de)

    # 5. Progression Clause (Progressionsvorbehalt)
    # Foreign income is added to determine the tax *rate*, but is not taxed itself.
    global_income_for_rate = taxable_income_de + foreign_income
    
    # Tax is calculated on the German income, but at the rate determined by global income.
    tax_on_global = calculate_german_tax(global_income_for_rate, is_married)
    effective_rate = tax_on_global / global_income_for_rate if global_income_for_rate > 0 else 0
    
    # 6. Final Tax Liability
    final_tax_liability = taxable_income_de * effective_rate
    net_german_tax_due = final_tax_liability - credits["total_credits"]
    net_german_tax_due = max(0, net_german_tax_due)
    
    # 7. Final Refund or Payment
    refund_or_payment = total_tax_paid - net_german_tax_due
    
    # 8. Compile and return the detailed report
    report = {
        # Raw Inputs
        "de_gross_a": de_gross_a, "de_tax_paid_a": de_tax_paid_a,
        "de_gross_b": de_gross_b, "de_tax_paid_b": de_tax_paid_b,
        "total_gross": total_gross, "total_tax_paid": total_tax_paid,
        "de_pension_a": data.get("de_pension_a", 0.0), "de_health_a": data.get("de_health_a", 0.0),
        "de_nursing_a": data.get("de_nursing_a", 0.0), "de_unemployment_a": data.get("de_unemployment_a", 0.0),
        "de_pension_b": data.get("de_pension_b", 0.0), "de_health_b": data.get("de_health_b", 0.0),
        "de_nursing_b": data.get("de_nursing_b", 0.0), "de_unemployment_b": data.get("de_unemployment_b", 0.0),
        
        # Deductions
        **deductions,
        
        # Credits
        **credits,
        
        # Calculation Steps
        "taxable_income_de": taxable_income_de,
        "foreign_income": foreign_income,
        "global_income_for_rate": global_income_for_rate,
        "effective_tax_rate": effective_rate,
        "final_tax_liability": final_tax_liability,
        "net_german_tax_due": net_german_tax_due,
        
        # Final Result
        "refund_or_payment": refund_or_payment,
        "tax_class": tax_class,
    }
    
    d_print("\n--- FINAL COMPILED REPORT ---")
    for key, value in report.items():
        d_print(f"  - {key}: {value:,.2f}" if isinstance(value, (int, float)) else f"  - {key}: {value}")
    d_print("-----------------------------\n")

    return report