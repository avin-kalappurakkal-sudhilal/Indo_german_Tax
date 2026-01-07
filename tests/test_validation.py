import unittest
import sys
import os

# Add the root directory of the project to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.report_generator import generate_full_report

class TestValidationEngine(unittest.TestCase):

    def test_social_security_warning(self):
        """
        Test that a warning is generated if social security contributions are zero
        for a significant German income.
        """
        form_data = {
            "is_married": False,
            "tax_class": 0, # Single
            "num_kids": 0,
            "de_gross_a": 50000, # Gross income > 20,000
            "de_tax_paid_a": 10000,
            "de_pension_a": 0, "de_health_a": 0, "de_nursing_a": 0, "de_unemployment_a": 0,
        }
        report = generate_full_report(form_data)
        self.assertIn(
            "Social security contributions seem missing. This will cause an overestimation of tax.",
            report["warnings"]
        )

    def test_tax_class_warning(self):
        """
        Test that a warning is generated if a user is married but the data indicates
        Tax Class 1 was selected. This simulates an inconsistent state that the
        validation should catch.
        """
        # This local re-implementation of generate_full_report allows us to test
        # the validation logic with inconsistent data that the UI aims to prevent.
        from logic.tax_calculator import calculate_german_tax
        from logic import constants

        def generate_report_with_dirty_tax_class(data):
            # In this version, we intentionally allow tax_class to be 1 if married
            # to test the validation warning.
            is_married = data.get("is_married", False)
            tax_class_index = data.get("tax_class", 0)
            tax_class = 1 if tax_class_index == 0 else tax_class_index + 3
            
            # The rest of the function is a simplified version of the original
            total_gross = data.get("de_gross_a", 0.0) + data.get("de_gross_b", 0.0)
            report = {"total_gross": total_gross, "tax_class": tax_class, "total_vorsorge": 10000, "final_tax_liability": 10000}
            
            from logic.report_generator import run_validation_checks
            report["warnings"] = run_validation_checks(data, report)
            return report

        form_data = {
            "is_married": True,
            "tax_class": 0, # In a 'single' context, this index means Class 1
            "num_kids": 0,
            "de_gross_a": 60000,
        }
        
        # We need to call a version of generate_full_report that can produce the state we want to test.
        # The actual generate_full_report sanitizes the tax class immediately.
        # We are testing the run_validation_checks function's ability to catch this.
        
        # Let's manually construct the context for the validation function
        from logic.report_generator import run_validation_checks
        report_context = {"tax_class": 1} # We simulate that the calculated class ended up as 1
        
        warnings = run_validation_checks(form_data, report_context)

        self.assertIn(
            "You are filing as married but using Tax Class 1. Tax Class 4 (Splitting) is usually more beneficial.",
            warnings
        )

    def test_child_benefit_note(self):
        """
        Test that a note about Child Allowance is added if the user has kids
        and the final tax liability is high.
        """
        form_data = {
            "is_married": True, "tax_class": 1, "num_kids": 2,
            "de_gross_a": 100000, "de_tax_paid_a": 25000,
            "de_pension_a": 8000, "de_health_a": 5000, "de_nursing_a": 1000, "de_unemployment_a": 1000,
            "de_gross_b": 50000, "de_tax_paid_b": 10000,
            "de_pension_b": 4000, "de_health_b": 2500, "de_nursing_b": 500, "de_unemployment_b": 500,
        }
        report = generate_full_report(form_data)
        if report["final_tax_liability"] > 3000:
            self.assertIn(
                "The tool has applied the Child Allowance (Kinderfreibetrag) as it was more beneficial than Kindergeld.",
                report["warnings"]
            )
        else:
            self.assertNotIn(
                "The tool has applied the Child Allowance (Kinderfreibetrag) as it was more beneficial than Kindergeld.",
                report["warnings"]
            )

    def test_no_warnings(self):
        """
        Test that no warnings are generated for a 'clean' data set.
        """
        form_data = {
            "is_married": True, "tax_class": 1, "num_kids": 0,
            "de_gross_a": 80000, "de_tax_paid_a": 20000,
            "de_pension_a": 7000, "de_health_a": 4500, "de_nursing_a": 800, "de_unemployment_a": 800,
        }
        report = generate_full_report(form_data)
        self.assertEqual(len(report["warnings"]), 0)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
