import sys
from PyQt6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QFormLayout, QDoubleSpinBox,
    QCheckBox, QGroupBox, QScrollArea, QWidget, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap

# ==========================================
# PART 1: BUSINESS LOGIC & DATA
# ==========================================

class TaxLogic:
    """Handles currency conversion and tax rules."""
    
    # Official Avg Exchange Rates (Approximate for example)
    # Source: Bundesfinanzministerium (umsatzsteuer-umrechnungskurse)
    EXCHANGE_RATES = {
        "2023": 0.0112,  # 1 INR = ~0.0112 EUR
        "2024": 0.0110   # Estimated
    }

    @staticmethod
    def convert_inr_to_eur(amount_inr, year="2023"):
        rate = TaxLogic.EXCHANGE_RATES.get(year, 0.011)
        return amount_inr * rate

    @staticmethod
    def get_form_mapping(data):
        """
        Maps collected data to specific German Tax Forms (Anlagen).
        Returns a list of instructions.
        """
        instructions = []
        
        # 1. Salary (Anlage N)
        if data['gross_salary'] > 0:
            instructions.append({
                "form": "Anlage N",
                "line": "Line 3 (Bruttoarbeitslohn)",
                "value": f"€ {data['gross_salary']:,.2f}",
                "note": "Copy directly from Lohnsteuerbescheinigung."
            })
            if data['werbungskosten'] > 1230:
                instructions.append({
                    "form": "Anlage N",
                    "line": "Lines 31-87 (Werbungskosten)",
                    "value": f"€ {data['werbungskosten']:,.2f}",
                    "note": "Total work-related expenses (Laptop, Commute, Training)."
                })

        # 2. German Capital (Anlage KAP)
        if data['de_capital_gains'] > 0:
            instructions.append({
                "form": "Anlage KAP",
                "line": "Line 7 (Kapitalerträge)",
                "value": f"€ {data['de_capital_gains']:,.2f}",
                "note": "Profit from Trade Republic/Scalable."
            })

        # 3. Indian Interest (Anlage KAP + AUS)
        if data['in_interest'] > 0:
            eur_val = TaxLogic.convert_inr_to_eur(data['in_interest'])
            instructions.append({
                "form": "Anlage KAP",
                "line": "Line 19 (Ausländische Kapitalerträge)",
                "value": f"€ {eur_val:,.2f}",
                "note": "Interest from NRE/NRO accounts (Taxable in DE)."
            })
            instructions.append({
                "form": "Anlage AUS",
                "line": "Table 1",
                "value": f"€ {eur_val:,.2f}",
                "note": "Declare here to claim credit for TDS paid in India."
            })

        # 4. Indian Rent (Anlage V + AUS)
        if data['in_rent'] > 0:
            eur_val = TaxLogic.convert_inr_to_eur(data['in_rent'])
            instructions.append({
                "form": "Anlage V / AUS",
                "line": "Foreign Income (Progressionsvorbehalt)",
                "value": f"€ {eur_val:,.2f}",
                "note": "This is NOT taxed directly, but raises your tax rate."
            })

        # 5. Support for Parents (Anlage Unterhalt)
        if data['parents_support'] > 0:
            instructions.append({
                "form": "Anlage Unterhalt",
                "line": "Support for needy persons",
                "value": f"€ {data['parents_support']:,.2f}",
                "note": "Requires 'Unterhaltserklärung' form signed by parents."
            })

        return instructions

# ==========================================
# PART 2: UI COMPONENTS (PAGES)
# ==========================================

class IntroPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to the Indo-German Tax Assistant")
        self.setSubTitle("A private, offline tool for Indian Expats in Germany.")

        layout = QVBoxLayout()
        
        info = QLabel(
            "<h3>Who is this for?</h3>"
            "<ul>"
            "<li>Indian Expats (Blue Card/PR) working in IT.</li>"
            "<li>Married couples with/without kids.</li>"
            "<li>People with assets in both India and Germany.</li>"
            "</ul>"
            "<br>"
            "<b>We will help you organize:</b><br>"
            "1. Lohnsteuerbescheinigung (German Salary)<br>"
            "2. Indian FDs & Savings (NRE/NRO)<br>"
            "3. Indian Rental Income & Stocks"
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Select Tax Year:"))
        self.year_combo = QComboBox()
        self.year_combo.addItems(["2023", "2024"])
        year_layout.addWidget(self.year_combo)
        layout.addLayout(year_layout)
        
        self.registerField("tax_year", self.year_combo)
        self.setLayout(layout)

class PersonalPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Step 1: Family & Tax Class")
        self.setSubTitle("Define your tax status.")

        layout = QFormLayout()

        # Marital Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Single", "Married (Living together in DE)", "Married (Spouse in India)"])
        layout.addRow("Marital Status:", self.status_combo)

        # Tax Class
        self.tax_class = QComboBox()
        self.tax_class.addItems(["I (Single)", "III / V (Married - Split)", "IV / IV (Married - Equal)"])
        self.tax_class.setToolTip("Check your payslip for 'Steuerklasse'.")
        layout.addRow("Tax Class:", self.tax_class)

        # Parents Support
        self.parents_support = QDoubleSpinBox()
        self.parents_support.setRange(0, 20000)
        self.parents_support.setPrefix("€ ")
        self.parents_support.setToolTip("Bank transfers made to parents in India for their maintenance.")
        layout.addRow("Support to Parents (Unterhalt):", self.parents_support)

        self.registerField("parents_support", self.parents_support)
        self.setLayout(layout)

class GermanIncomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Step 2: German Income")
        self.setSubTitle("Grab your 'Lohnsteuerbescheinigung' (Annual Tax Cert).")

        layout = QFormLayout()

        self.gross = QDoubleSpinBox()
        self.gross.setRange(0, 500000)
        self.gross.setPrefix("€ ")
        layout.addRow("Gross Salary (Line 3):", self.gross)

        self.tax_paid = QDoubleSpinBox()
        self.tax_paid.setRange(0, 200000)
        self.tax_paid.setPrefix("€ ")
        layout.addRow("Tax Paid (Line 4):", self.tax_paid)

        # Expenses
        self.expenses = QDoubleSpinBox()
        self.expenses.setRange(0, 50000)
        self.expenses.setPrefix("€ ")
        self.expenses.setValue(1230) # Standard lump sum
        self.expenses.setToolTip("Laptop, Internet, Commute, Moving Costs. Minimum is €1230.")
        layout.addRow("Work Expenses (Werbungskosten):", self.expenses)

        # German Stocks
        self.de_stocks = QDoubleSpinBox()
        self.de_stocks.setRange(0, 1000000)
        self.de_stocks.setPrefix("€ ")
        self.de_stocks.setToolTip("Profit from Trade Republic, Scalable, ING, etc.")
        layout.addRow("German Capital Gains:", self.de_stocks)

        self.registerField("gross_salary", self.gross)
        self.registerField("werbungskosten", self.expenses)
        self.registerField("de_capital_gains", self.de_stocks)
        self.setLayout(layout)

class IndianIncomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Step 3: Indian Income (DTAA)")
        self.setSubTitle("Enter amounts in INR (₹). We will convert them.")

        layout = QFormLayout()

        # Section 1: Interest
        lbl_int = QLabel("<b>A. Savings & FDs (NRE/NRO)</b>")
        layout.addRow(lbl_int)
        
        self.in_interest = QDoubleSpinBox()
        self.in_interest.setRange(0, 100000000)
        self.in_interest.setPrefix("₹ ")
        self.in_interest.setToolTip("Total Interest credited in FY (April-March). Check Form 26AS or Interest Cert.")
        layout.addRow("Total Interest (NRE + NRO):", self.in_interest)

        # Warning
        warn_lbl = QLabel("<small style='color:red'>Note: NRE Interest is taxable in Germany even if tax-free in India.</small>")
        layout.addRow("", warn_lbl)

        # Section 2: Rent
        lbl_rent = QLabel("<b>B. Rental Income</b>")
        layout.addRow(lbl_rent)

        self.in_rent = QDoubleSpinBox()
        self.in_rent.setRange(0, 100000000)
        self.in_rent.setPrefix("₹ ")
        layout.addRow("Net Rental Income:", self.in_rent)
        
        rent_note = QLabel("<small>Rent - (Property Tax + Maintenance + Standard Deduction).</small>")
        layout.addRow("", rent_note)

        # Section 3: Stocks
        lbl_stock = QLabel("<b>C. Indian Stocks/Mutual Funds</b>")
        layout.addRow(lbl_stock)

        self.in_stocks = QDoubleSpinBox()
        self.in_stocks.setRange(0, 100000000)
        self.in_stocks.setPrefix("₹ ")
        layout.addRow("Capital Gains (Sold):", self.in_stocks)

        self.registerField("in_interest", self.in_interest)
        self.registerField("in_rent", self.in_rent)
        self.registerField("in_stocks", self.in_stocks)
        
        self.setLayout(layout)

class SummaryPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Final Checklist & Next Steps")
        self.setSubTitle("Here is where your data goes.")

    def initializePage(self):
        # Gather Data
        data = {
            'gross_salary': self.field('gross_salary'),
            'werbungskosten': self.field('werbungskosten'),
            'de_capital_gains': self.field('de_capital_gains'),
            'in_interest': self.field('in_interest'),
            'in_rent': self.field('in_rent'),
            'in_stocks': self.field('in_stocks'),
            'parents_support': self.field('parents_support')
        }

        # Replace None with 0 for numeric fields to avoid TypeErrors
        for key in data:
            if data[key] is None:
                data[key] = 0

        # Get Instructions
        instructions = TaxLogic.get_form_mapping(data)

        # Build UI dynamically
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout()

        # Header
        content_layout.addWidget(QLabel("<h3> Filing Instructions </h3>"))

        if not instructions:
            content_layout.addWidget(QLabel("No complex data entered. Basic declaration only."))
        else:
            # Create a Card for each instruction
            for item in instructions:
                box = QGroupBox(item['form'])
                box_layout = QFormLayout()
                
                val_lbl = QLabel(f"<b>{item['value']}</b>")
                val_lbl.setStyleSheet("color: #2c3e50; font-size: 14px;")
                
                box_layout.addRow("Field/Line:", QLabel(item['line']))
                box_layout.addRow("Value to Enter:", val_lbl)
                box_layout.addRow("Note:", QLabel(f"<i>{item['note']}</i>"))
                
                box.setLayout(box_layout)
                content_layout.addWidget(box)

        # ELSTER Info
        elster_lbl = QLabel(
            "<hr><b>Recommended Software:</b><br>"
            "1. ELSTER (Free, German only)<br>"
            "2. Wundertax / Taxfix (English, paid)<br>"
            "3. SteuerGo (English, paid)"
        )
        content_layout.addWidget(elster_lbl)

        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.setLayout(layout)

# ==========================================
# PART 3: MAIN APP CONTROLLER
# ==========================================

class TaxAssistantApp(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Indo-German Tax Assistant")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.resize(900, 700)

        # Add Pages
        self.addPage(IntroPage())
        self.addPage(PersonalPage())
        self.addPage(GermanIncomePage())
        self.addPage(IndianIncomePage())
        self.addPage(SummaryPage())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Global Styling (CSS)
    app.setStyleSheet("""
        QWizard { background-color: #ffffff; }
        QGroupBox { 
            border: 1px solid #bdc3c7; 
            border-radius: 5px; 
            margin-top: 10px; 
            font-weight: bold;
        }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
        QLabel { font-size: 13px; }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox { 
            padding: 6px; 
            border: 1px solid #ccc; 
            border-radius: 4px;
            background-color: #f9f9f9;
        }
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 0; }
    """)

    window = TaxAssistantApp()
    window.show()
    sys.exit(app.exec())