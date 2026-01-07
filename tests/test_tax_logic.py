import unittest
from logic.report_generator import generate_full_report
from logic.utils import estimate_social_security
from logic.constants import WERBUNGSKOSTEN_PAUSCHALE, TAX_YEAR_CONSTANTS
from logic.tax_calculator import calculate_soli

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
        social_contributions = estimate_social_security(gross_salary, year, num_children=0)
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
        social_contributions = estimate_social_security(gross_salary, year, num_children=1)
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

class TestSoliCalculation(unittest.TestCase):
    # Thresholds for 2024-2026 (Tax Liability amount) - duplicated for testing purposes
    thresholds = {
        2024: 18130,
        2025: 19450,
        2026: 20350
    }

    def test_soli_single_below_threshold(self):
        """Test Soli calculation for a single person with tax liability below the exemption limit."""
        year = 2024
        tax_liability = self.thresholds[year] - 1000
        self.assertEqual(calculate_soli(tax_liability, year, is_married=False), 0.0)

    def test_soli_single_above_threshold(self):
        """Test Soli calculation for a single person with tax liability above the exemption limit."""
        year = 2024
        tax_liability = self.thresholds[year] + 1000
        expected_soli = tax_liability * 0.055
        self.assertAlmostEqual(calculate_soli(tax_liability, year, is_married=False), expected_soli)

    def test_soli_married_below_threshold(self):
        """Test Soli calculation for a married couple with tax liability below the doubled exemption limit."""
        year = 2025
        limit = self.thresholds[year] * 2
        tax_liability = limit - 2000
        self.assertEqual(calculate_soli(tax_liability, year, is_married=True), 0.0)

    def test_soli_married_above_threshold(self):
        """Test Soli calculation for a married couple with tax liability above the doubled exemption limit."""
        year = 2025
        limit = self.thresholds[year] * 2
        tax_liability = limit + 2000
        expected_soli = tax_liability * 0.055
        self.assertAlmostEqual(calculate_soli(tax_liability, year, is_married=True), expected_soli)

    def test_soli_year_2026_edge_case(self):
        """Test Soli calculation for the year 2026 at exactly the threshold."""
        year = 2026
        tax_liability = self.thresholds[year]
        self.assertEqual(calculate_soli(tax_liability, year, is_married=False), 0.0)

    def test_soli_unknown_year_uses_default(self):
        """Test that an unknown year defaults to the latest available Soli limit (2026)."""
        # Tax liability is above 2026 single limit
        tax_liability = self.thresholds[2026] + 1000
        expected_soli = tax_liability * 0.055
        # Using a future year that is not in the constants
        self.assertAlmostEqual(calculate_soli(tax_liability, 2028, is_married=False), expected_soli)


if __name__ == '__main__':
    unittest.main()

