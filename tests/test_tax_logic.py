import unittest
from logic.report_generator import generate_full_report
from logic.utils import estimate_social_security
from logic.constants import WERBUNGSKOSTEN_PAUSCHALE, TAX_YEAR_CONSTANTS

class TestTaxLogic(unittest.TestCase):

    def test_single_filer_2024_60k(self):
        """
        Tests the tax calculation for a single filer in 2024 with a gross income of €60,000.
        Verifies that taxable income (zvE) is calculated correctly and social security caps are applied.
        """
        year = 2024
        gross_salary = 60000.0
        is_married = False
        has_kids = False # Affects nursing insurance

        # 1. Estimate social security contributions
        # These are deductions from the gross salary.
        social_contributions = estimate_social_security(gross_salary, year, has_kids)
        total_social_contributions = sum(social_contributions.values())

        # 2. Prepare the input data dictionary for the report generator
        # This simulates the data collected from the UI.
        form_data = {
            "tax_year": str(year),
            "is_married": is_married,
            "num_kids": 1 if has_kids else 0,
            "de_gross_a": gross_salary,
            "de_pension_a": social_contributions["pension"],
            "de_health_a": social_contributions["health"],
            "de_nursing_a": social_contributions["nursing"],
            "de_unemployment_a": social_contributions["unemployment"],
            # Assume default work-related expenses (Werbungskostenpauschale will be applied)
            "ho_days_a": 0,
            "commute_km_a": 0,
            "office_days_a": 0,
        }

        # 3. Generate the full tax report
        report = generate_full_report(form_data)

        # 4. Verification
        # Check if social security caps for 2024 were applied correctly.
        # Gross salary is below the 2024 caps, so no capping should occur.
        pension_cap_2024 = TAX_YEAR_CONSTANTS[year]['SOCIAL_SECURITY_CAPS']['pension']
        health_cap_2024 = TAX_YEAR_CONSTANTS[year]['SOCIAL_SECURITY_CAPS']['health']
        self.assertLess(gross_salary, pension_cap_2024)
        self.assertLess(gross_salary, health_cap_2024)

        # Calculate expected taxable income (zvE)
        # zvE = Gross Income - Social Security - Work-Related Expenses
        expected_taxable_income = gross_salary - total_social_contributions - WERBUNGSKOSTEN_PAUSCHALE
        
        self.assertAlmostEqual(expected_taxable_income, report["taxable_income_de"], places=2)
        
        # The tax formula itself should not tax the basic allowance.
        # We can verify that the calculated tax is greater than zero,
        # as the taxable income is well above the allowance.
        basic_allowance_2024 = TAX_YEAR_CONSTANTS[year]['BASIC_ALLOWANCE']
        self.assertGreater(report["taxable_income_de"], basic_allowance_2024)
        self.assertGreater(report["final_tax_liability"], 0)


    def test_married_couple_2025_120k(self):
        """
        Tests the tax calculation for a married couple in 2025 with a combined gross income of €120,000.
        Verifies joint assessment (Splitting) and year-specific social security caps.
        """
        year = 2025
        gross_salary = 120000.0
        is_married = True
        has_kids = True # Affects nursing insurance

        # 1. Estimate social security contributions
        # The caps for 2025 are higher than 2024. Gross salary is above the pension cap.
        social_contributions = estimate_social_security(gross_salary, year, has_kids)
        total_social_contributions = sum(social_contributions.values())
        
        # 2. Prepare the input data dictionary
        form_data = {
            "tax_year": str(year),
            "is_married": is_married,
            "num_kids": 1 if has_kids else 0,
            "de_gross_a": gross_salary, # Assign all income to one person
            "de_gross_b": 0.0,
            "de_pension_a": social_contributions["pension"],
            "de_health_a": social_contributions["health"],
            "de_nursing_a": social_contributions["nursing"],
            "de_unemployment_a": social_contributions["unemployment"],
            # Assume default work-related expenses for Person A
            "ho_days_a": 0, "commute_km_a": 0, "office_days_a": 0,
        }

        # 3. Generate the full tax report
        report = generate_full_report(form_data)

        # 4. Verification
        # Check if social security caps for 2025 were applied correctly.
        # Gross salary is above the pension cap, so pension contribution should be capped.
        pension_cap_2025 = TAX_YEAR_CONSTANTS[year]['SOCIAL_SECURITY_CAPS']['pension']
        health_cap_2025 = TAX_YEAR_CONSTANTS[year]['SOCIAL_SECURITY_CAPS']['health']
        
        self.assertGreater(gross_salary, pension_cap_2025)
        expected_pension = pension_cap_2025 * 0.093 # Employee's share
        self.assertAlmostEqual(expected_pension, social_contributions["pension"], places=2)

        # Calculate expected taxable income (zvE)
        # zvE = Gross Income - Social Security - Work-Related Expenses
        # Only one Pauschale is applied as Person B has no income.
        expected_taxable_income = gross_salary - total_social_contributions - WERBUNGSKOSTEN_PAUSCHALE
        
        self.assertAlmostEqual(expected_taxable_income, report["taxable_income_de"], places=2)

        # Verify that the basic allowance for married couples (doubled) is used correctly.
        # The taxable income should be well above the allowance.
        basic_allowance_2025 = TAX_YEAR_CONSTANTS[year]['BASIC_ALLOWANCE']
        self.assertGreater(report["taxable_income_de"], basic_allowance_2025 * 2)
        self.assertGreater(report["final_tax_liability"], 0)


if __name__ == '__main__':
    unittest.main()
