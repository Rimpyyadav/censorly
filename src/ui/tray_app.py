"""
System Tray Application
Provides user interface via system tray icon
"""

from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, 
                              QWidget, QVBoxLayout, QLabel, QPushButton,
                              QSlider, QCheckBox, QComboBox, QHBoxLayout)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer
import sys
import os


class TrayApplication(QSystemTrayIcon):
    """System tray application"""
    
    def __init__(self, streamblur_app, qt_app):  # ← Add qt_app parameter
        # Don't create QApplication here - use the one passed in
        self.qt_app = qt_app
        
        # Create icon
        icon = self.create_icon()
        super().__init__(icon, self.qt_app)
        
        self.streamblur = streamblur_app
        
        # Rest stays the same...
        # Create menu
        self.create_menu()
        
        # Show tray icon
        self.setVisible(True)
        self.setToolTip("StreamBlur - Privacy Protection")
        
        # Connect signals
        self.activated.connect(self.on_tray_activated)
        
        # Show notification
        self.showMessage("StreamBlur", "StreamBlur is running! Right-click tray icon for menu.", 
                        QSystemTrayIcon.MessageIcon.Information, 3000)
        
        print("✅ System Tray initialized")
    
    def create_icon(self):
        """Create a simple icon"""
        # Create a 64x64 blue square icon
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.blue)
        return QIcon(pixmap)
    
    def create_menu(self):
        """Create right-click menu"""
        menu = QMenu()
        
        # Blur mode submenu
        blur_menu = QMenu("Blur Mode", menu)
        
        self.blur_off_action = QAction("Off", blur_menu)
        self.blur_off_action.setCheckable(True)
        self.blur_off_action.triggered.connect(lambda: self.set_blur_mode("none"))
        blur_menu.addAction(self.blur_off_action)
        
        self.blur_full_action = QAction("Full Screen", blur_menu)
        self.blur_full_action.setCheckable(True)
        self.blur_full_action.triggered.connect(lambda: self.set_blur_mode("full"))
        blur_menu.addAction(self.blur_full_action)
        
        self.blur_regions_action = QAction("Smart Regions ⭐", blur_menu)
        self.blur_regions_action.setCheckable(True)
        self.blur_regions_action.setChecked(True)
        self.blur_regions_action.triggered.connect(lambda: self.set_blur_mode("regions"))
        blur_menu.addAction(self.blur_regions_action)
        
        menu.addMenu(blur_menu)
        menu.addSeparator()
        
        # OCR toggle
        self.ocr_action = QAction("Enable OCR Detection", menu)
        self.ocr_action.setCheckable(True)
        self.ocr_action.setChecked(True)  # Default on
        self.ocr_action.triggered.connect(self.toggle_ocr)
        menu.addAction(self.ocr_action)
        
        # Virtual Camera toggle
        self.vcam_action = QAction("Enable Virtual Camera", menu)
        self.vcam_action.setCheckable(True)
        self.vcam_action.triggered.connect(self.toggle_vcam)
        menu.addAction(self.vcam_action)
        
        # Preview Window toggle
        self.preview_action = QAction("Show Preview Window", menu)
        self.preview_action.setCheckable(True)
        self.preview_action.triggered.connect(self.toggle_preview)
        menu.addAction(self.preview_action)
        
        menu.addSeparator()
        
        # Settings
        settings_action = QAction("Settings...", menu)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        # Statistics
        stats_action = QAction("Statistics", menu)
        stats_action.triggered.connect(self.show_stats)
        menu.addAction(stats_action)
        
        menu.addSeparator()
        
        # Exit
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(self.quit_app)
        menu.addAction(exit_action)
        
        self.setContextMenu(menu)
    
    def update_menu_state(self):
        """Update menu checkboxes based on current state"""
        mode = self.streamblur.blur_mode
        self.blur_off_action.setChecked(mode == "none")
        self.blur_full_action.setChecked(mode == "full")
        self.blur_regions_action.setChecked(mode == "regions")
        
        self.ocr_action.setChecked(self.streamblur.ocr_enabled)
        self.vcam_action.setChecked(self.streamblur.vcam_enabled)
        self.preview_action.setChecked(self.streamblur.show_preview)
    
    def set_blur_mode(self, mode):
        """Set blur mode"""
        self.streamblur.set_blur_mode(mode)
        self.update_menu_state()
        self.showMessage("StreamBlur", f"Blur mode: {mode.upper()}", 
                        QSystemTrayIcon.MessageIcon.Information, 2000)
    
    def toggle_ocr(self):
        """Toggle OCR"""
        self.streamblur.toggle_ocr()
        self.update_menu_state()
        status = "enabled" if self.streamblur.ocr_enabled else "disabled"
        self.showMessage("StreamBlur", f"OCR {status}", 
                        QSystemTrayIcon.MessageIcon.Information, 2000)
    
    def toggle_vcam(self):
        """Toggle virtual camera"""
        self.streamblur.toggle_vcam()
        self.update_menu_state()
        status = "enabled" if self.streamblur.vcam_enabled else "disabled"
        self.showMessage("StreamBlur", f"Virtual Camera {status}", 
                        QSystemTrayIcon.MessageIcon.Information, 2000)
    
    def toggle_preview(self):
        """Toggle preview window"""
        self.streamblur.toggle_preview()
        self.update_menu_state()
        status = "shown" if self.streamblur.show_preview else "hidden"
        self.showMessage("StreamBlur", f"Preview window {status}", 
                        QSystemTrayIcon.MessageIcon.Information, 2000)
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.streamblur)
        dialog.show()  # Use show() instead of exec()
    
    def show_stats(self):
        """Show statistics"""
        stats = f"""StreamBlur Statistics

Total Frames: {self.streamblur.total_frames}
Total Detections: {self.streamblur.total_detections}
Current FPS: {self.streamblur.capturer.get_fps():.1f}

Blur Mode: {self.streamblur.blur_mode.upper()}
OCR: {'ON' if self.streamblur.ocr_enabled else 'OFF'}
Virtual Camera: {'ON' if self.streamblur.vcam_enabled else 'OFF'}
        """
        self.showMessage("StreamBlur Statistics", stats.strip(), 
                        QSystemTrayIcon.MessageIcon.Information, 5000)
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_settings()
    
    def quit_app(self):
        """Quit application"""
        print("\n🛑 Quitting from tray...")
        self.streamblur.stop()
        self.qt_app.quit()
    
    def run(self):
        """Run Qt application"""
        return self.qt_app.exec()


class SettingsDialog(QWidget):
    """Settings dialog window"""
    
    def __init__(self, streamblur_app, qt_app):
        super().__init__()
        self.streamblur = streamblur_app
        self.qt_app = qt_app
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("StreamBlur Settings")
        self.setGeometry(100, 100, 400, 500)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("StreamBlur Settings")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Blur Mode
        layout.addWidget(QLabel("\n🔵 Blur Mode:"))
        self.blur_combo = QComboBox()
        self.blur_combo.addItems(["Off", "Full Screen", "Smart Regions"])
        mode_index = {"none": 0, "full": 1, "regions": 2}.get(self.streamblur.blur_mode, 0)
        self.blur_combo.setCurrentIndex(mode_index)
        self.blur_combo.currentIndexChanged.connect(self.on_blur_mode_changed)
        layout.addWidget(self.blur_combo)
        
        # Blur Strength
        layout.addWidget(QLabel("\n🎚️ Blur Strength:"))
        strength_layout = QHBoxLayout()
        self.strength_slider = QSlider(Qt.Orientation.Horizontal)
        self.strength_slider.setMinimum(1)
        self.strength_slider.setMaximum(10)
        self.strength_slider.setValue(self.streamblur.renderer.blur_strength)
        self.strength_slider.valueChanged.connect(self.on_strength_changed)
        self.strength_label = QLabel(str(self.streamblur.renderer.blur_strength))
        strength_layout.addWidget(self.strength_slider)
        strength_layout.addWidget(self.strength_label)
        layout.addLayout(strength_layout)
        
        # OCR Detection
        layout.addWidget(QLabel("\n📝 Detection:"))
        self.ocr_checkbox = QCheckBox("Enable OCR Detection")
        self.ocr_checkbox.setChecked(self.streamblur.ocr_enabled)
        self.ocr_checkbox.stateChanged.connect(self.on_ocr_changed)
        layout.addWidget(self.ocr_checkbox)
        
        # Virtual Camera
        layout.addWidget(QLabel("\n📹 Output:"))
        self.vcam_checkbox = QCheckBox("Enable Virtual Camera")
        self.vcam_checkbox.setChecked(self.streamblur.vcam_enabled)
        self.vcam_checkbox.stateChanged.connect(self.on_vcam_changed)
        layout.addWidget(self.vcam_checkbox)
        
        # Detection Boxes
        self.boxes_checkbox = QCheckBox("Show Detection Boxes")
        self.boxes_checkbox.setChecked(self.streamblur.show_detection_boxes)
        self.boxes_checkbox.stateChanged.connect(self.on_boxes_changed)
        layout.addWidget(self.boxes_checkbox)
        
        # Preview Window
        self.preview_checkbox = QCheckBox("Show Preview Window")
        self.preview_checkbox.setChecked(self.streamblur.show_preview)
        self.preview_checkbox.stateChanged.connect(self.on_preview_changed)
        layout.addWidget(self.preview_checkbox)
        
        # Statistics
        layout.addWidget(QLabel("\n📊 Statistics:"))
        stats_text = f"""Frames Processed: {self.streamblur.total_frames}
Detections: {self.streamblur.total_detections}
Current FPS: {self.streamblur.capturer.get_fps():.1f}
        """
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("background-color: #f0f0f0; padding: 10px;")
        layout.addWidget(stats_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_blur_mode_changed(self, index):
        """Handle blur mode change"""
        modes = ["none", "full", "regions"]
        self.streamblur.set_blur_mode(modes[index])
    
    def on_strength_changed(self, value):
        """Handle strength change"""
        self.strength_label.setText(str(value))
        self.streamblur.renderer.set_blur_strength(value)
    
    def on_ocr_changed(self, state):
        """Handle OCR toggle"""
        should_be_on = (state == Qt.CheckState.Checked.value)
        if should_be_on != self.streamblur.ocr_enabled:
            self.streamblur.toggle_ocr()
    
    def on_vcam_changed(self, state):
        """Handle virtual camera toggle"""
        should_be_on = (state == Qt.CheckState.Checked.value)
        if should_be_on != self.streamblur.vcam_enabled:
            self.streamblur.toggle_vcam()
    
    def on_boxes_changed(self, state):
        """Handle detection boxes toggle"""
        self.streamblur.show_detection_boxes = (state == Qt.CheckState.Checked.value)
    
    def on_preview_changed(self, state):
        """Handle preview toggle"""
        should_show = (state == Qt.CheckState.Checked.value)
        if should_show != self.streamblur.show_preview:
            self.streamblur.toggle_preview()