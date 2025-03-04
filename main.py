import sys
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QTabWidget, QPushButton, QLabel,
                            QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Import our custom modules
from modules.pdf_editor import PDFEditorTab
from modules.pdf_merger import PDFMergerTab
from modules.pdf_splitter import PDFSplitterTab
from modules.pdf_converter import PDFConverterTab
from modules.ocr import OCRTab
from modules.license_manager import LicenseManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professional PDF Editor")
        self.setMinimumSize(1200, 800)
        
        # Initialize license manager
        self.license_manager = LicenseManager()
        
        # Check trial/license status
        self.check_license_status()
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Add various feature tabs
        self.tabs.addTab(PDFEditorTab(), "Edit PDF")
        self.tabs.addTab(PDFMergerTab(), "Merge PDFs")
        self.tabs.addTab(PDFSplitterTab(), "Split PDF")
        self.tabs.addTab(PDFConverterTab(), "Convert PDF")
        self.tabs.addTab(OCRTab(), "OCR")
        
        # Add tabs to layout
        layout.addWidget(self.tabs)
        
        # Create status bar
        self.setup_status_bar()
    
    def setup_status_bar(self):
        status_bar = self.statusBar()
        
        # Add license status
        if self.license_manager.is_trial():
            days_left = self.license_manager.get_trial_days_left()
            status_bar.showMessage(f"Trial Version - {days_left} days remaining")
        elif self.license_manager.is_licensed():
            status_bar.showMessage("Licensed Version")
        else:
            status_bar.showMessage("License Expired - Please Purchase")
    
    def check_license_status(self):
        if not self.license_manager.is_valid():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("License Status")
            
            if self.license_manager.is_trial():
                days_left = self.license_manager.get_trial_days_left()
                msg.setText(f"You are using the trial version.\n{days_left} days remaining.")
                msg.setInformativeText("Would you like to purchase a license now?")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                
                if msg.exec() == QMessageBox.StandardButton.Yes:
                    self.license_manager.show_purchase_dialog()
            else:
                msg.setText("Your trial has expired.")
                msg.setInformativeText("Please purchase a license to continue using the software.")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                
                # Show purchase dialog
                self.license_manager.show_purchase_dialog()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a modern look
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
