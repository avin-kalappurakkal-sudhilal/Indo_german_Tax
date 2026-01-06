import sys
from PyQt6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QFormLayout, QDoubleSpinBox,
    QCheckBox, QGroupBox, QScrollArea, QWidget, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

# ==========================================
# PART 1: UI PAGES
# ==========================================

class IntroPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Indo-German Tax Assistant 2026")
        self.setSubTitle("A private tool for IT expats with families and global assets.")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(
            "This tool will calculate your tax position based on:<br>"
            "1. <b>German Salary:</b> From your Lohnsteuerbescheinigung.<br>"
            "2. <b>Family:</b> Wife, Kids, and Support to Parents in India.<br>"
            "3. <b>Indian Income:</b> NRE/NRO Interest, Rent, and Stocks.<br><br>"
            "<i>Everything is calculated locally on your computer.</i>"
        ))
        self.setLayout(layout)

class PersonalFamilyPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Step 1: Family & Tax Status")
        layout = QFormLayout()

        self.tax_class = QComboBox()
        self.tax_class.addItems(["1 (Single)", "3 (Married - Main Earner)", "4 (Married - Equal)", "5 (Married - Partner)"])
        layout.addRow("Tax Class (Steuerklasse):", self.tax_class)

        self.num_kids = QDoubleSpinBox()
        self.num_kids.setDecimals(0)
        layout.addRow("Number of Kids:", self.num_kids)

        self.parents_support = QDoubleSpinBox()
        self.parents_support.setRange(0, 50000)
        self.parents_support.setPrefix("€ ")
        self.parents_support.setToolTip("Money sent to parents in India via bank transfer for their living costs.")
        layout.addRow("Support to Parents (Unterhalt):", self.parents_support)

        # Register Fields
        self.registerField("tax_class*", self.tax_class)
        self.registerField("num_kids", self.num_kids, "value")
        self.registerField("parents_support", self.parents_support, "value")
        self.setLayout(layout)

class GermanIncomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Step 2: German Employment Income")
        layout = QFormLayout()

        self.gross = QDoubleSpinBox()
        self.gross.setRange(0, 1000000)
        self.gross.setPrefix("€ ")
        layout.addRow("Annual Gross Salary (Line 3):", self.gross)

        self.tax_paid = QDoubleSpinBox()
        self.tax_paid.setRange(0, 500000)
        self.tax_paid.setPrefix("€ ")
        layout.addRow("Income Tax Already Paid (Line 4):", self.tax_paid)

        self.registerField("de_gross", self.gross, "value")
        self.registerField("de_tax_paid", self.tax_paid, "value")
        self.setLayout(layout)

class IndianIncomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Step 3: Indian Income (DTAA Rules)")
        layout = QFormLayout()

        self.in_rent = QDoubleSpinBox()
        self.in_rent.setRange(0, 10000000)
        self.in_rent.setPrefix("₹ ")
        layout.addRow("Net Indian Rent (Annual):", self.in_rent)

        self.in_interest = QDoubleSpinBox()
        self.in_interest.setRange(0, 10000000)
        self.in_interest.setPrefix("₹ ")
        layout.addRow("Indian Bank Interest (NRE/NRO):", self.in_interest)

        self.registerField("in_rent", self.in_rent, "value")
        self.registerField("in_interest", self.in_interest, "value")
        self.setLayout(layout)

class DeductionsPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Step 4: Tax-Saving Deductions")
        layout = QFormLayout()

        # Work Deductions
        layout.addWidget(QLabel("<b>Work-Related Expenses (Werbungskosten)</b>"))
        self.work_equipment = QDoubleSpinBox()
        self.work_equipment.setPrefix("€ ")
        self.work_equipment.setRange(0, 10000)
        layout.addRow("Work Equipment (Laptop/Furniture):", self.work_equipment)

        self.training_costs = QDoubleSpinBox()
        self.training_costs.setPrefix("€ ")
        self.training_costs.setRange(0, 20000)
        layout.addRow("Professional Training/Certs:", self.training_costs)
        
        self.commute_km = QDoubleSpinBox()
        self.commute_km.setDecimals(1)
        layout.addRow("One-way Distance to Office (km):", self.commute_km)

        self.office_days = QDoubleSpinBox()
        self.office_days.setDecimals(0)
        self.office_days.setRange(0, 230)
        layout.addRow("Actual Days spent in Office:", self.office_days)

        self.home_office_days = QDoubleSpinBox()
        self.home_office_days.setRange(0, 220)
        self.home_office_days.setDecimals(0)
        layout.addRow("Home Office Days (pauschal €6/day):", self.home_office_days)

        self.moving_costs = QCheckBox("Did you move from a non-EU country for this job?")
        layout.addRow(self.moving_costs)

        # Family & Home Deductions
        layout.addWidget(QLabel("<b>Family & Home Expenses</b>"))
        self.kita_costs = QDoubleSpinBox()
        self.kita_costs.setRange(0, 20000)
        self.kita_costs.setPrefix("€ ")
        layout.addRow("Annual Kita/Childcare Costs:", self.kita_costs)

        self.nebenkosten_labor = QDoubleSpinBox()
        self.nebenkosten_labor.setRange(0, 10000)
        self.nebenkosten_labor.setPrefix("€ ")
        self.nebenkosten_labor.setToolTip("Total labor costs from your Nebenkostenabrechnung (Section 35a summary).")
        layout.addRow("Ancillary Labor Costs (Sec 35a):", self.nebenkosten_labor)

        # Indian Tax Credit (Crucial for DTAA)
        layout.addWidget(QLabel("<b>Foreign Tax Credits</b>"))
        self.in_tds = QDoubleSpinBox()
        self.in_tds.setRange(0, 1000000)
        self.in_tds.setPrefix("₹ ")
        self.in_tds.setToolTip("Enter the total TDS deducted in India (from Form 26AS).")
        layout.addRow("TDS Paid in India (on NRO/Rent):", self.in_tds)

        self.registerField("work_equipment", self.work_equipment, "value")
        self.registerField("training_costs", self.training_costs, "value")
        self.registerField("commute_km", self.commute_km, "value")
        self.registerField("office_days", self.office_days, "value")
        self.registerField("ho_days", self.home_office_days, "value")
        self.registerField("is_moving", self.moving_costs, "checked")
        self.registerField("kita_costs", self.kita_costs, "value")
        self.registerField("nk_labor", self.nebenkosten_labor, "value")
        self.registerField("in_tds_inr", self.in_tds, "value")
        self.setLayout(layout)

class ResultPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Final Outcome & Action Plan")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def calculate_german_tax(self, zvE, is_married=True):
        """
        Official German Tax Formula (Approx 2024/2025)
        zvE = taxable income (zu versteuerndes Einkommen)
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

    def initializePage(self):
        # 1. Gather All Data
        de_gross = self.field("de_gross") or 0.0
        de_tax_paid = self.field("de_tax_paid") or 0.0
        in_rent_eur = (self.field("in_rent") or 0.0) * 0.011
        in_interest_eur = (self.field("in_interest") or 0.0) * 0.011
        parents_eur = self.field("parents_support") or 0.0
        is_married = (self.field("tax_class") or 0) != 0
        
        # Deductions Data
        ho_days = self.field("ho_days") or 0.0
        is_moving = self.field("is_moving") or False
        kita_costs = self.field("kita_costs") or 0.0
        nk_labor_costs = self.field("nk_labor") or 0.0
        in_tds_eur = (self.field("in_tds_inr") or 0.0) * 0.011
        work_equipment = self.field("work_equipment") or 0.0
        training_costs = self.field("training_costs") or 0.0
        commute_km = self.field("commute_km") or 0.0
        office_days = self.field("office_days") or 0.0

        print("\n--- DEBUG: GATHERED RAW DATA ---")
        print(f"  de_gross: {de_gross}")
        print(f"  de_tax_paid: {de_tax_paid}")
        print(f"  in_rent (EUR): {in_rent_eur}")
        print(f"  in_interest (EUR): {in_interest_eur}")
        print(f"  parents_support (€): {parents_eur}")
        print(f"  is_married (Index != 0): {is_married}")
        print(f"  ho_days: {ho_days}")
        print(f"  is_moving: {is_moving}")
        print(f"  kita_costs (€): {kita_costs}")
        print(f"  nebenkosten_labor (€): {nk_labor_costs}")
        print(f"  in_tds (EUR): {in_tds_eur}")
        print(f"  work_equipment (€): {work_equipment}")
        print(f"  training_costs (€): {training_costs}")
        print(f"  commute_km: {commute_km}")
        print(f"  office_days: {office_days}")
        print("------------------------------------")

        # 2. Calculate Deductions & Taxable Income
        ho_deduction = ho_days * 6.0
        moving_lump_sum = 890.0 if is_moving else 0.0
        kita_deduction = kita_costs * (2/3)
        
        commute_deduction = 0
        if commute_km <= 20:
            commute_deduction = commute_km * 0.30 * office_days
        else:
            commute_deduction = (20 * 0.30 + (commute_km - 20) * 0.38) * office_days

        itemized_werbungskosten = (
            ho_deduction +
            moving_lump_sum +
            work_equipment +
            training_costs +
            commute_deduction +
            16 +  # Bank fee flat rate
            240  # Internet/Phone flat rate
        )

        werbungskosten = max(1230, itemized_werbungskosten)
        
        other_deductions = kita_deduction + parents_eur
        
        taxable_income_de = de_gross - werbungskosten - other_deductions
        if taxable_income_de < 0: taxable_income_de = 0

        # 3. Logic: Progression Clause (Progressionsvorbehalt)
        global_income = taxable_income_de + in_rent_eur + in_interest_eur
        if global_income < 0: global_income = 0
        
        tax_on_global = self.calculate_german_tax(global_income, is_married)
        effective_rate = tax_on_global / global_income if global_income > 0 else 0
        
        # 4. Calculate Final Tax & Refund
        final_tax_liability = taxable_income_de * effective_rate
        
        # Tax Credits
        nk_credit = nk_labor_costs * 0.20
        total_credits = in_tds_eur + nk_credit
        
        net_german_tax_due = final_tax_liability - total_credits
        if net_german_tax_due < 0: net_german_tax_due = 0
        
        refund_or_payment = de_tax_paid - net_german_tax_due

        print("\n--- DEBUG: CALCULATION RESULTS ---")
        print(f"  Total Werbungskosten: {werbungskosten}")
        print(f"  Other Deductions (Kita, Parents): {other_deductions}")
        print(f"  Taxable German Income (zvE): {taxable_income_de}")
        print(f"  Global Income (for rate): {global_income}")
        print(f"  Effective Tax Rate: {effective_rate:.4f}")
        print(f"  Final Tax Liability: {final_tax_liability}")
        print(f"  TDS Credit (€): {in_tds_eur}")
        print(f"  Ancillary Labor Credit (€): {nk_credit}")
        print(f"  Net German Tax Due: {net_german_tax_due}")
        print(f"  >> REFUND / (PAYMENT): {refund_or_payment}")
        print("-------------------------------------\n")

        # 5. Update UI
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        self.result_html = (
            f"<h2>Tax Filing Roadmap</h2>"
            f"<p><b>Total German Gross:</b> €{de_gross:,.2f}</p>"
            f"<p><b>Total Deductions:</b> €{(werbungskosten + other_deductions):,.2f}</p>"
            f"<p><b>Taxable German Income (zvE):</b> €{taxable_income_de:,.2f}</p>"
            f"<hr>"
            f"<p><b>Foreign Income (for rate):</b> €{(in_rent_eur + in_interest_eur):,.2f}</p>"
            f"<p><b>Effective Tax Rate (Progressionsvorbehalt):</b> {effective_rate*100:.2f}%</p>"
            f"<p><b>Calculated German Tax:</b> €{final_tax_liability:,.2f}</p>"
            f"<p style='color:blue;'><b>- Credit for Tax Paid in India (TDS):</b> €{in_tds_eur:,.2f}</p>"
            f"<p style='color:blue;'><b>- Credit for Ancillary Labor Costs:</b> €{nk_credit:,.2f}</p>"
            f"<h3>Net German Tax Due: €{net_german_tax_due:,.2f}</h3>"
            f"<hr>"
            f"<p><b>Tax Already Paid in Germany (Lohnsteuer):</b> €{de_tax_paid:,.2f}</p>"
        )
        
        if refund_or_payment > 0:
            self.result_html += f"<h2 style='color:green;'>ESTIMATED REFUND: €{refund_or_payment:,.2f}</h2>"
        else:
            self.result_html += f"<h2 style='color:red;'>ESTIMATED ADDITIONAL PAYMENT: €{abs(refund_or_payment):,.2f}</h2>"

        outcome_label = QLabel(self.result_html)
        outcome_label.setWordWrap(True)
        self.layout.addWidget(outcome_label)

        # Add Save Button
        save_button = QPushButton("Save Report to File")
        save_button.clicked.connect(self.save_report)
        self.layout.addWidget(save_button)

    def save_report(self):
        if not hasattr(self, 'result_html') or not self.result_html:
            QMessageBox.warning(self, "No Data", "There is no report data to save yet.")
            return
        
        # Convert HTML to plain text for the report
        import re
        report_text = self.result_html
        report_text = report_text.replace("<h2>", "== ").replace("</h2>", " ==\n")
        report_text = report_text.replace("<h3>", "--- ").replace("</h3>", " ---\n")
        report_text = report_text.replace("<p>", "").replace("</p>", "\n")
        report_text = report_text.replace("<hr>", "--------------------------------\n")
        report_text = report_text.replace("<b>", "").replace("</b>", "")
        report_text = re.sub(r'<p style=[^>]+>', '', report_text) # Remove styled p tags

        file_path = "German_Tax_Report.txt"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("INDO-GERMAN TAX REPORT\n")
                f.write("========================\n\n")
                f.write(report_text)
            QMessageBox.information(self, "Success", f"Report saved successfully to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save report: {e}")

# ==========================================
# PART 2: MAIN APP
# ==========================================

class TaxApp(QWizard):
    def __init__(self):
        super().__init__()
        self.addPage(IntroPage())
        self.addPage(PersonalFamilyPage())
        self.addPage(GermanIncomePage())
        self.addPage(IndianIncomePage())
        self.addPage(DeductionsPage())
        self.addPage(ResultPage())
        self.setWindowTitle("Indo-German Expat Tax Tool")
        self.resize(800, 700)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaxApp()
    window.show()
    sys.exit(app.exec())