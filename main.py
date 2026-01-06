import sys
from PyQt6.QtWidgets import QApplication, QWizard

from ui.pages import (
    IntroPage, PersonalFamilyPage, GermanIncomePage, 
    IndianIncomePage, DeductionsPage, ResultPage
)

class TaxApp(QWizard):
    """
    Main application window, a QWizard that guides the user through tax-related pages.
    """
    def __init__(self):
        super().__init__()
        # Add all the UI pages to the wizard in the correct order
        self.addPage(IntroPage())
        self.addPage(PersonalFamilyPage())
        self.addPage(GermanIncomePage())
        self.addPage(IndianIncomePage())
        self.addPage(DeductionsPage())
        self.addPage(ResultPage())
        
        self.setWindowTitle("Indo-German Expat Tax Tool")
        self.resize(800, 700)

def main():
    """
    Main function to initialize and run the PyQt application.
    """
    app = QApplication(sys.argv)
    window = TaxApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
