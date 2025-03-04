import fitz
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QFileDialog, QScrollArea, QColorDialog,
                            QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor
import os
from PIL import Image
import io

class PDFEditorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_pdf = None
        self.current_page = 0
        self.current_page_pixmap = None
        self.zoom_factor = 1.0
        self.setup_ui()
        
        # Drawing state
        self.is_drawing = False
        self.last_point = None
        self.current_color = QColor(255, 255, 0, 128)  # Semi-transparent yellow
        self.current_tool = 'highlight'
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # File operations
        self.open_btn = QPushButton("Open PDF")
        self.open_btn.clicked.connect(self.open_pdf)
        toolbar.addWidget(self.open_btn)
        
        self.save_btn = QPushButton("Save PDF")
        self.save_btn.clicked.connect(self.save_pdf)
        self.save_btn.setEnabled(False)
        toolbar.addWidget(self.save_btn)
        
        # Tool selection
        self.highlight_btn = QPushButton("Highlight")
        self.highlight_btn.clicked.connect(lambda: self.set_tool('highlight'))
        toolbar.addWidget(self.highlight_btn)
        
        self.underline_btn = QPushButton("Underline")
        self.underline_btn.clicked.connect(lambda: self.set_tool('underline'))
        toolbar.addWidget(self.underline_btn)
        
        self.text_btn = QPushButton("Add Text")
        self.text_btn.clicked.connect(self.add_text)
        toolbar.addWidget(self.text_btn)
        
        self.signature_btn = QPushButton("Add Signature")
        self.signature_btn.clicked.connect(self.add_signature)
        toolbar.addWidget(self.signature_btn)
        
        # Color picker
        self.color_btn = QPushButton("Color")
        self.color_btn.clicked.connect(self.choose_color)
        toolbar.addWidget(self.color_btn)
        
        # Navigation
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setEnabled(False)
        toolbar.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        toolbar.addWidget(self.next_btn)
        
        self.page_label = QLabel("Page: 0/0")
        toolbar.addWidget(self.page_label)
        
        layout.addLayout(toolbar)
        
        # PDF display area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.pdf_label)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
    
    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "", "PDF files (*.pdf)"
        )
        if file_path:
            try:
                self.current_pdf = fitz.open(file_path)
                self.current_page = 0
                self.update_page_display()
                self.save_btn.setEnabled(True)
                self.prev_btn.setEnabled(True)
                self.next_btn.setEnabled(True)
                self.page_label.setText(f"Page: 1/{len(self.current_pdf)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open PDF: {str(e)}")
    
    def save_pdf(self):
        if not self.current_pdf:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", "", "PDF files (*.pdf)"
        )
        if file_path:
            try:
                self.current_pdf.save(file_path)
                QMessageBox.information(self, "Success", "PDF saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save PDF: {str(e)}")
    
    def update_page_display(self):
        if not self.current_pdf:
            return
        
        page = self.current_pdf[self.current_page]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        # Convert to QImage
        img = QImage(pix.samples, pix.width, pix.height,
                    pix.stride, QImage.Format.Format_RGB888)
        
        # Convert to QPixmap and display
        pixmap = QPixmap.fromImage(img)
        self.current_page_pixmap = pixmap
        self.pdf_label.setPixmap(pixmap.scaled(
            self.pdf_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
    
    def next_page(self):
        if self.current_pdf and self.current_page < len(self.current_pdf) - 1:
            self.current_page += 1
            self.update_page_display()
            self.page_label.setText(
                f"Page: {self.current_page + 1}/{len(self.current_pdf)}"
            )
    
    def prev_page(self):
        if self.current_pdf and self.current_page > 0:
            self.current_page -= 1
            self.update_page_display()
            self.page_label.setText(
                f"Page: {self.current_page + 1}/{len(self.current_pdf)}"
            )
    
    def set_tool(self, tool):
        self.current_tool = tool
    
    def choose_color(self):
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
    
    def add_text(self):
        if not self.current_pdf:
            return
        
        text, ok = QInputDialog.getText(
            self, "Add Text", "Enter text to add:"
        )
        if ok and text:
            page = self.current_pdf[self.current_page]
            # Add text at center of page (you can modify position as needed)
            rect = page.rect
            page.insert_text(
                (rect.width / 2, rect.height / 2),
                text,
                fontsize=12,
                color=(0, 0, 0)
            )
            self.update_page_display()
    
    def add_signature(self):
        if not self.current_pdf:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Signature Image", "",
            "Image files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            try:
                # Open and resize signature image
                img = Image.open(file_path)
                img.thumbnail((200, 100))  # Resize to reasonable dimensions
                
                # Convert to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes = img_bytes.getvalue()
                
                # Add to PDF
                page = self.current_pdf[self.current_page]
                rect = page.rect
                page.insert_image(
                    (rect.width / 2, rect.height / 2),  # Center of page
                    stream=img_bytes
                )
                self.update_page_display()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Could not add signature: {str(e)}"
                )
    
    def mousePressEvent(self, event):
        if not self.current_pdf or not self.current_page_pixmap:
            return
        
        self.is_drawing = True
        self.last_point = event.pos()
    
    def mouseReleaseEvent(self, event):
        self.is_drawing = False
    
    def mouseMoveEvent(self, event):
        if not self.is_drawing or not self.current_pdf:
            return
        
        page = self.current_pdf[self.current_page]
        
        # Convert screen coordinates to PDF coordinates
        scale_x = page.rect.width / self.current_page_pixmap.width()
        scale_y = page.rect.height / self.current_page_pixmap.height()
        
        start = self.last_point
        end = event.pos()
        
        # Add annotation based on current tool
        if self.current_tool == 'highlight':
            page.add_highlight_annot(
                (start.x() * scale_x, start.y() * scale_y,
                 end.x() * scale_x, end.y() * scale_y)
            )
        elif self.current_tool == 'underline':
            page.add_underline_annot(
                (start.x() * scale_x, start.y() * scale_y,
                 end.x() * scale_x, end.y() * scale_y)
            )
        
        self.last_point = end
        self.update_page_display()
