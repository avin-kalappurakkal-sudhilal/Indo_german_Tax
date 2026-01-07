import re
from PyQt6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QFormLayout, QDoubleSpinBox,
    QCheckBox, QGroupBox, QScrollArea, QWidget, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from logic.report_generator import generate_full_report

# ==========================================
# UI PAGES
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

        self.married_checkbox = QCheckBox("Filing jointly as a married couple")
        self.married_checkbox.stateChanged.connect(self.update_tax_classes)
        layout.addRow(self.married_checkbox)

        self.tax_class = QComboBox()
        layout.addRow("Tax Class (Steuerklasse):", self.tax_class)

        self.num_kids = QDoubleSpinBox()
        self.num_kids.setDecimals(0)
        layout.addRow("Number of Kids:", self.num_kids)

        self.parents_support = QDoubleSpinBox()
        self.parents_support.setRange(0, 50000)
        self.parents_support.setPrefix("\u20ac ")
        self.parents_support.setToolTip("Money sent to parents in India via bank transfer for their living costs.")
        layout.addRow("Support to Parents (Unterhalt):", self.parents_support)

        # Register Fields
        self.registerField("is_married", self.married_checkbox)
        self.registerField("tax_class", self.tax_class, "currentIndex", self.tax_class.currentIndexChanged)
        self.registerField("num_kids", self.num_kids, "value", self.num_kids.valueChanged)
        self.registerField("parents_support", self.parents_support, "value", self.parents_support.valueChanged)
        
        self.setLayout(layout)
        self.update_tax_classes() # Set initial state

    def update_tax_classes(self):
        is_married = self.married_checkbox.isChecked()
        self.tax_class.clear()
        if is_married:
            self.tax_class.addItems(["3 (Married - Main Earner)", "4 (Married - Equal)", "5 (Married - Partner)"])
        else:
            self.tax_class.addItems(["1 (Single)"])

class GermanIncomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Step 2: German Employment Income (Lohnsteuerbescheinigung)")
        main_layout = QHBoxLayout(self)

        # PERSON A COLUMN
        group_a = QGroupBox("Person A (Main Earner)")
        layout_a = QFormLayout()

        self.gross_a = QDoubleSpinBox(); self.gross_a.setRange(0, 1000000); self.gross_a.setPrefix("\u20ac ")
        self.tax_paid_a = QDoubleSpinBox(); self.tax_paid_a.setRange(0, 500000); self.tax_paid_a.setPrefix("\u20ac ")
        self.pension_a = QDoubleSpinBox(); self.pension_a.setRange(0, 100000); self.pension_a.setPrefix("\u20ac ")
        self.health_a = QDoubleSpinBox(); self.health_a.setRange(0, 50000); self.health_a.setPrefix("\u20ac ")
        self.nursing_a = QDoubleSpinBox(); self.nursing_a.setRange(0, 10000); self.nursing_a.setPrefix("\u20ac ")
        self.unemployment_a = QDoubleSpinBox(); self.unemployment_a.setRange(0, 10000); self.unemployment_a.setPrefix("\u20ac ")

        layout_a.addRow("Annual Gross Salary (Line 3):", self.gross_a)
        layout_a.addRow("Income Tax Paid (Line 4):", self.tax_paid_a)
        layout_a.addRow("Pension Insurance (22a/23a):", self.pension_a)
        layout_a.addRow("Health Insurance (25):", self.health_a)
        layout_a.addRow("Nursing Care Insurance (26):", self.nursing_a)
        layout_a.addRow("Unemployment Insurance (27):", self.unemployment_a)
        group_a.setLayout(layout_a)

        # PERSON B COLUMN
        group_b = QGroupBox("Person B (Spouse)")
        layout_b = QFormLayout()

        self.gross_b = QDoubleSpinBox(); self.gross_b.setRange(0, 1000000); self.gross_b.setPrefix("\u20ac ")
        self.tax_paid_b = QDoubleSpinBox(); self.tax_paid_b.setRange(0, 500000); self.tax_paid_b.setPrefix("\u20ac ")
        self.pension_b = QDoubleSpinBox(); self.pension_b.setRange(0, 100000); self.pension_b.setPrefix("\u20ac ")
        self.health_b = QDoubleSpinBox(); self.health_b.setRange(0, 50000); self.health_b.setPrefix("\u20ac ")
        self.nursing_b = QDoubleSpinBox(); self.nursing_b.setRange(0, 10000); self.nursing_b.setPrefix("\u20ac ")
        self.unemployment_b = QDoubleSpinBox(); self.unemployment_b.setRange(0, 10000); self.unemployment_b.setPrefix("\u20ac ")

        layout_b.addRow("Annual Gross Salary (Line 3):", self.gross_b)
        layout_b.addRow("Income Tax Paid (Line 4):", self.tax_paid_b)
        layout_b.addRow("Pension Insurance (22a/23a):", self.pension_b)
        layout_b.addRow("Health Insurance (25):", self.health_b)
        layout_b.addRow("Nursing Care Insurance (26):", self.nursing_b)
        layout_b.addRow("Unemployment Insurance (27):", self.unemployment_b)
        group_b.setLayout(layout_b)

        main_layout.addWidget(group_a)
        main_layout.addWidget(group_b)

        # Register Fields for Person A
        self.registerField("de_gross_a*", self.gross_a, "value", self.gross_a.valueChanged)
        self.registerField("de_tax_paid_a*", self.tax_paid_a, "value", self.tax_paid_a.valueChanged)
        self.registerField("de_pension_a", self.pension_a, "value", self.pension_a.valueChanged)
        self.registerField("de_health_a", self.health_a, "value", self.health_a.valueChanged)
        self.registerField("de_nursing_a", self.nursing_a, "value", self.nursing_a.valueChanged)
        self.registerField("de_unemployment_a", self.unemployment_a, "value", self.unemployment_a.valueChanged)
        
        # Register Fields for Person B
        self.registerField("de_gross_b", self.gross_b, "value", self.gross_b.valueChanged)
        self.registerField("de_tax_paid_b", self.tax_paid_b, "value", self.tax_paid_b.valueChanged)
        self.registerField("de_pension_b", self.pension_b, "value", self.pension_b.valueChanged)
        self.registerField("de_health_b", self.health_b, "value", self.health_b.valueChanged)
        self.registerField("de_nursing_b", self.nursing_b, "value", self.nursing_b.valueChanged)
        self.registerField("de_unemployment_b", self.unemployment_b, "value", self.unemployment_b.valueChanged)


class IndianIncomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Step 3: Indian Income (DTAA Rules)")
        layout = QFormLayout()

        self.in_rent = QDoubleSpinBox()
        self.in_rent.setRange(0, 10000000)
        self.in_rent.setPrefix("\u20b9 ")
        layout.addRow("Net Indian Rent (Annual):", self.in_rent)

        self.in_interest = QDoubleSpinBox()
        self.in_interest.setRange(0, 10000000)
        self.in_interest.setPrefix("\u20b9 ")
        layout.addRow("Indian Bank Interest (NRE/NRO):", self.in_interest)

        self.registerField("in_rent", self.in_rent, "value", self.in_rent.valueChanged)
        self.registerField("in_interest", self.in_interest, "value", self.in_interest.valueChanged)
        self.setLayout(layout)

class DeductionsPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Step 4: Tax-Saving Deductions")
        main_layout = QVBoxLayout(self)

        # Work-Related Expenses (Werbungskosten)
        work_expenses_group = QGroupBox("Work-Related Expenses (Werbungskosten)")
        cols_layout = QHBoxLayout()
        
        # Person A Group
        group_a = QGroupBox("Person A (You)")
        lay_a = QFormLayout()
        self.commute_a = QDoubleSpinBox(); self.commute_a.setRange(0, 300); self.commute_a.setDecimals(1)
        self.days_a = QDoubleSpinBox(); self.days_a.setRange(0, 230); self.days_a.setDecimals(0)
        self.ho_a = QDoubleSpinBox(); self.ho_a.setRange(0, 210); self.ho_a.setDecimals(0)
        self.internet_a = QDoubleSpinBox(); self.internet_a.setRange(0, 500); self.internet_a.setPrefix("\u20ac "); self.internet_a.setValue(240.0)
        self.bank_fee_a_cb = QCheckBox("Apply Bank Account Flat Rate (\u20ac16)")

        lay_a.addRow("Commute (one way, km):", self.commute_a)
        lay_a.addRow("Work Office Days:", self.days_a)
        lay_a.addRow("Home Office Days:", self.ho_a)
        lay_a.addRow("Internet/Phone (professional use):", self.internet_a)
        lay_a.addRow(self.bank_fee_a_cb)
        group_a.setLayout(lay_a)
        
        # Person B Group
        group_b = QGroupBox("Person B (Spouse)")
        lay_b = QFormLayout()
        self.commute_b = QDoubleSpinBox(); self.commute_b.setRange(0, 300); self.commute_b.setDecimals(1)
        self.days_b = QDoubleSpinBox(); self.days_b.setRange(0, 230); self.days_b.setDecimals(0)
        self.ho_b = QDoubleSpinBox(); self.ho_b.setRange(0, 210); self.ho_b.setDecimals(0)
        self.internet_b = QDoubleSpinBox(); self.internet_b.setRange(0, 500); self.internet_b.setPrefix("\u20ac "); self.internet_b.setValue(240.0)
        self.bank_fee_b_cb = QCheckBox("Apply Bank Account Flat Rate (\u20ac16)")

        lay_b.addRow("Commute (one way, km):", self.commute_b)
        lay_b.addRow("Work Office Days:", self.days_b)
        lay_b.addRow("Home Office Days:", self.ho_b)
        lay_b.addRow("Internet/Phone (professional use):", self.internet_b)
        lay_b.addRow(self.bank_fee_b_cb)
        group_b.setLayout(lay_b)
        
        cols_layout.addWidget(group_a)
        cols_layout.addWidget(group_b)
        work_expenses_group.setLayout(cols_layout)
        main_layout.addWidget(work_expenses_group)

        # Shared Household & Other Expenses
        shared_group = QGroupBox("Shared Household & Other Expenses")
        lay_s = QFormLayout()
        self.kita = QDoubleSpinBox(); self.kita.setRange(0, 20000); self.kita.setPrefix("\u20ac ")
        self.nk_labor = QDoubleSpinBox(); self.nk_labor.setRange(0, 10000); self.nk_labor.setPrefix("\u20ac ")
        self.tds = QDoubleSpinBox(); self.tds.setRange(0, 1000000); self.tds.setPrefix("\u20b9 ")
        
        lay_s.addRow("Childcare/Kita Costs (max \u20ac6000 per child):", self.kita)
        lay_s.addRow("Labor Costs in Nebenkosten (\u00a735a):", self.nk_labor)
        lay_s.addRow("Indian TDS (if any, in \u20b9):", self.tds)
        shared_group.setLayout(lay_s)
        main_layout.addWidget(shared_group)

        # Field Registration
        self.registerField("commute_km_a", self.commute_a)
        self.registerField("office_days_a", self.days_a)
        self.registerField("ho_days_a", self.ho_a)
        self.registerField("internet_a", self.internet_a)
        self.registerField("bank_fee_a", self.bank_fee_a_cb)

        self.registerField("commute_km_b", self.commute_b)
        self.registerField("office_days_b", self.days_b)
        self.registerField("ho_days_b", self.ho_b)
        self.registerField("internet_b", self.internet_b)
        self.registerField("bank_fee_b", self.bank_fee_b_cb)

        self.registerField("kita_costs", self.kita)
        self.registerField("nk_labor", self.nk_labor)
        self.registerField("in_tds_inr", self.tds)

class ResultPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Final Outcome & Action Plan")
        self.layout = QVBoxLayout(self)
        
        # Use a QScrollArea for potentially long reports
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.result_label = QLabel("Calculating...")
        self.result_label.setWordWrap(True)
        self.result_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        scroll_area.setWidget(self.result_label)
        
        self.layout.addWidget(scroll_area)
        
        self.save_button = QPushButton("Save Report to File")
        self.save_button.clicked.connect(self.save_report)
        self.layout.addWidget(self.save_button)
        
        self.report_data = None

    def initializePage(self):
        # 1. Gather all data from wizard fields
        field_names = [
            "is_married", "tax_class", "num_kids", "parents_support",
            # Person A
            "de_gross_a", "de_tax_paid_a",
            "de_pension_a", "de_health_a", "de_nursing_a", "de_unemployment_a",
            "commute_km_a", "office_days_a", "ho_days_a", "internet_a", "bank_fee_a",
            # Person B
            "de_gross_b", "de_tax_paid_b",
            "de_pension_b", "de_health_b", "de_nursing_b", "de_unemployment_b",
            "commute_km_b", "office_days_b", "ho_days_b", "internet_b", "bank_fee_b",
            # Shared
            "in_rent", "in_interest",
            "kita_costs", "nk_labor", "in_tds_inr",
        ]
        
        form_data = {}
        for name in field_names:
            value = self.field(name)
            if value is not None:
                form_data[name] = value
            else:
                # Assign default for fields that may not exist or haven't been visited
                form_data[name] = 0.0 if "bank_fee" not in name else False

        # 2. Generate the full report from the logic module
        self.report_data = generate_full_report(form_data)
        
        # 3. Format and display the results
        self.display_report()

    def display_report(self):
        r = self.report_data
        
        refund_or_payment_text = (
            f"<h2 style='color:green;'>ESTIMATED REFUND: {r['refund_or_payment']:,.2f}\u20ac</h2>"
            if r['refund_or_payment'] > 0
            else f"<h2 style='color:red;'>ESTIMATED ADDITIONAL PAYMENT: {abs(r['refund_or_payment']):,.2f}\u20ac</h2>"
        )
        
        is_married = (self.field("tax_class") or 0) != 0

        # Detailed breakdown table
        details_html = f"""
        <table border="1" style="width:100%; border-collapse: collapse; font-size: 10pt;">
            <tr style="background-color:#e6e6fa;">
                <th style="padding: 6px; text-align: left;">Item</th>
                <th style="padding: 6px; text-align: right;">Person A (You)</th>
                <th style="padding: 6px; text-align: right;">Person B (Spouse)</th>
                <th style="padding: 6px; text-align: right;">JOINT TOTAL</th>
            </tr>
            <tr>
                <td style="padding: 6px;"><b>Annual Gross Income</b></td>
                <td style="padding: 6px; text-align: right;">{r['de_gross_a']:,.2f}\u20ac</td>
                <td style="padding: 6px; text-align: right;">{r['de_gross_b']:,.2f}\u20ac</td>
                <td style="padding: 6px; text-align: right;"><b>{r['total_gross']:,.2f}\u20ac</b></td>
            </tr>
            <tr style="background-color:#f2f2f2;">
                <td style="padding: 6px;" colspan="4"><b>(-) Mandatory Social Security (Vorsorgeaufwendungen)</b></td>
            </tr>
            <tr>
                <td style="padding: 6px;">Pension Insurance</td>
                <td style="padding: 6px; text-align: right;">-{r['de_pension_a']:,.2f}\u20ac</td>
                <td style="padding: 6px; text-align: right;">-{r['de_pension_b']:,.2f}\u20ac</td>
                <td style="padding: 6px; text-align: right;"></td>
            </tr>
            <tr>
                <td style="padding: 6px;">Health Insurance</td>
                <td style="padding: 6px; text-align: right;">-{r['de_health_a']:,.2f}\u20ac</td>
                <td style="padding: 6px; text-align: right;">-{r['de_health_b']:,.2f}\u20ac</td>
                <td style="padding: 6px; text-align: right;"></td>
            </tr>
             <tr>
                <td style="padding: 6px;">Nursing Care Insurance</td>
                <td style="padding: 6px; text-align: right;">-{r['de_nursing_a']:,.2f}\u20ac</td>
                <td style="padding: 6px; text-align: right;">-{r['de_nursing_b']:,.2f}\u20ac</td>
                <td style="padding: 6px; text-align: right;"></td>
            </tr>
             <tr>
                <td style="padding: 6px;">Unemployment Insurance</td>
                <td style="padding: 6px; text-align: right;">-{r['de_unemployment_a']:,.2f}\u20ac</td>
                <td style="padding: 6px; text-align: right;">-{r['de_unemployment_b']:,.2f}\u20ac</td>
                <td style="padding: 6px; text-align: right;"></td>
            </tr>
            <tr style="font-weight:bold;">
                <td style="padding: 6px;">Total Social Security</td>
                <td style="padding: 6px; text-align: right;"></td>
                <td style="padding: 6px; text-align: right;"></td>
                <td style="padding: 6px; text-align: right;">-{r['total_vorsorge']:,.2f}\u20ac</td>
            </tr>
            <tr style="background-color:#f2f2f2;">
                <td style="padding: 6px;" colspan="4"><b>(-) Work Expenses & Deductions (Werbungskosten / Pauschalen)</b></td>
            </tr>
            <tr>
                <td style="padding: 6px;">Income-Related Expenses (Werbungskosten)</td>
                <td style="padding: 6px; text-align: right;">-{r['wk_a']:,.2f}\u20ac</td>
                <td style="padding: 6px; text-align: right;">-{r['wk_b']:,.2f}\u20ac</td>
                <td style="padding: 6px; text-align: right;"></td>
            </tr>
             <tr>
                <td style="padding: 6px;">Other Deductions (Parents, Kita etc.)</td>
                <td style="padding: 6px; text-align: right;"></td>
                <td style="padding: 6px; text-align: right;"></td>
                <td style="padding: 6px; text-align: right;">-{r['other_deductions']:,.2f}\u20ac</td>
            </tr>
            <tr style="background-color:#e6e6fa; font-weight:bold;">
                <td style="padding: 6px;">= Taxable Income (Germany)</td>
                <td style="padding: 6px; text-align: right;"></td>
                <td style="padding: 6px; text-align: right;"></td>
                <td style="padding: 6px; text-align: right;">{r['taxable_income_de']:,.2f}\u20ac</td>
            </tr>
        </table>
        """
        
        summary_html = f"""
        <h3>Tax Calculation Summary</h3>
        <p><b>(+) Foreign Income (for rate calculation):</b> {r['foreign_income']:,.2f}\u20ac</p>
        <p><b>(=) Global Income for Rate:</b> {r['global_income_for_rate']:,.2f}\u20ac</p>
        <p><b>(&rarr;) Effective Tax Rate (Progressionsvorbehalt):</b> {r['effective_tax_rate']*100:.2f}%</p>
        <hr>
        <p><b>Calculated German Tax on Taxable Income:</b> {r['final_tax_liability']:,.2f}\u20ac</p>
        <p style='color:blue;'><b>(-) Credit for Ancillary Labor Costs (\u00a735a):</b> -{r['nebenkosten_credit']:,.2f}\u20ac</p>
        <p style='color:blue;'><b>(-) Credit for Tax Paid in India (TDS):</b> -{r['tds_credit']:,.2f}\u20ac</p>
        <h3>Net German Tax Due: {r['net_german_tax_due']:,.2f}\u20ac</h3>
        <hr>
        <p><b>Tax Already Paid in Germany (Lohnsteuer):</b> {r['total_tax_paid']:,.2f}\u20ac</p>
        {refund_or_payment_text}
        """

        html = f"<h2>Tax Filing Roadmap</h2>{details_html}<br>{summary_html}"
        self.result_label.setText(html)

    def save_report(self):
        if not self.report_data:
            QMessageBox.warning(self, "No Data", "There is no report data to save yet.")
            return

        r = self.report_data
        refund_or_payment_label = "ESTIMATED REFUND" if r['refund_or_payment'] > 0 else "ESTIMATED ADDITIONAL PAYMENT"
        
        report_text = (
            "INDO-GERMAN TAX REPORT (DUAL INCOME)\n"
            "=======================================\n\n"
            f"DISCLAIMER: This is a non-binding estimate. Consult a tax advisor.\n\n"
            "--- INCOME SUMMARY ---\n"
            f"Person A - Gross: {r['de_gross_a']:>15,.2f}\u20ac\n"
            f"Person B - Gross: {r['de_gross_b']:>15,.2f}\u20ac\n"
            f"JOINT GROSS:      {r['total_gross']:>15,.2f}\u20ac\n\n"
            "--- DEDUCTIONS & TAXABLE INCOME ---\n"
            f"(-) Total Social Security: {r['total_vorsorge']:>9,.2f}\u20ac\n"
            f"(-) Total Work Expenses (WK): {r['total_wk']:>6,.2f}\u20ac\n"
            f"(-) Other Deductions:      {r['other_deductions']:>9,.2f}\u20ac\n"
            f"---------------------------------------\n"
            f"(=) TAXABLE GERMAN INCOME (zvE): {r['taxable_income_de']:>1,.2f}\u20ac\n\n"
            "--- TAX CALCULATION ---\n"
            f"(+) Foreign Income (for rate):   {r['foreign_income']:>5,.2f}\u20ac\n"
            f"(&rarr;) Effective Tax Rate:            {r['effective_tax_rate']*100:>7.2f}%\n"
            f"---------------------------------------\n"
            f"(=) Calculated German Tax:       {r['final_tax_liability']:>5,.2f}\u20ac\n"
            f"(-) Credits (\u00a735a, TDS):         -{r['total_credits']:>5,.2f}\u20ac\n"
            f"---------------------------------------\n"
            f"(=) NET GERMAN TAX DUE:          {r['net_german_tax_due']:>5,.2f}\u20ac\n\n"
            "--- FINAL RESULT ---\n"
            f"Tax Already Paid (Lohnsteuer):   {r['total_tax_paid']:>5,.2f}\u20ac\n"
            f"--- {refund_or_payment_label}: {abs(r['refund_or_payment']):>9,.2f}\u20ac ---\n"
        )
        
        file_path = "German_Tax_Report.txt"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report_text)
            QMessageBox.information(self, "Success", f"Report saved successfully to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save report: {e}")
