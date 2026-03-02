"""
StreamBlur - Tray Application
Day 9-10: System Tray UI
"""

import sys

# Add src to path
sys.path.insert(0, 'src')

from capture.screen_capture import ScreenCapture
from detection.detection_manager import DetectionManager
from rendering.blur_renderer import BlurRenderer
from core.app_runner import AppRunner

# Try to import virtual camera
try:
    from output.virtual_camera import VirtualCamera
    VIRTUAL_CAM_AVAILABLE = True
except ImportError:
    from output.virtual_camera import VirtualCameraFallback as VirtualCamera
    VIRTUAL_CAM_AVAILABLE = False


class StreamBlurApp:
    """StreamBlur Application - For Tray UI"""
    
    def __init__(self):
        print("\n🚀 Initializing StreamBlur with System Tray UI...")
        print("━" * 60)
        
        # Initialize components
        self.capturer = ScreenCapture(monitor_index=1, target_fps=30)
        self.detector = DetectionManager()
        self.renderer = BlurRenderer(blur_strength=7)
        
        # Virtual camera
        width, height = self.capturer.get_resolution()
        self.vcam = VirtualCamera(width=width, height=height, fps=30)
        
        # Settings
        self.blur_mode = "regions"  # Default to smart mode
        self.ocr_enabled = True      # Default OCR on
        self.vcam_enabled = False
        self.show_detection_boxes = False
        self.show_preview = True
        self.running = True
        
        # Performance
        self.frame_count = 0
        self.ocr_interval = 5
        self.sensitive_regions = []
        
        # Stats
        self.total_frames = 0
        self.total_detections = 0
        
        print("✅ StreamBlur initialized!")
        print("   Look for the blue icon in your system tray →")
        print("━" * 60 + "\n")
    
    def process_detection(self, frame):
        """Run detection"""
        self.sensitive_regions = self.detector.detect_sensitive_regions(frame)
        if self.sensitive_regions:
            self.total_detections += len(self.sensitive_regions)
    
    def render_frame(self, frame):
        """Apply blur"""
        if self.blur_mode == "full":
            return self.renderer.blur_full_frame(frame)
        elif self.blur_mode == "regions" and self.sensitive_regions:
            return self.renderer.blur_regions_with_padding(
                frame, self.sensitive_regions, padding=15
            )
        return frame
    
    def add_overlay(self, frame):
        """Add overlay"""
        import cv2
        
        y_pos = 30
        
        # FPS
        cv2.putText(frame, f'FPS: {self.capturer.get_fps():.1f}', 
                    (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        y_pos += 35
        
        # Blur mode
        blur_colors = {"none": (128, 128, 128), "full": (255, 165, 0), "regions": (0, 255, 0)}
        cv2.putText(frame, f"Blur: {self.blur_mode.upper()}", (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, blur_colors.get(self.blur_mode, (255, 255, 255)), 2)
        y_pos += 35
        
        # Status
        cv2.putText(frame, f"OCR: {'ON' if self.ocr_enabled else 'OFF'}", (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                    (0, 255, 0) if self.ocr_enabled else (128, 128, 128), 2)
        y_pos += 30
        
        cv2.putText(frame, f"VCam: {'ON' if self.vcam_enabled else 'OFF'}", (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 0) if self.vcam_enabled else (128, 128, 128), 2)
        y_pos += 30
        
        # Detections
        if self.sensitive_regions:
            cv2.putText(frame, f"⚠️ Blurred: {len(self.sensitive_regions)}", 
                        (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        
        return frame
    
    def set_blur_mode(self, mode):
        """Set blur mode"""
        self.blur_mode = mode
        print(f"🔵 Blur Mode: {mode.upper()}")
    
    def toggle_ocr(self):
        """Toggle OCR"""
        self.ocr_enabled = not self.ocr_enabled
        if not self.ocr_enabled:
            self.sensitive_regions = []
        print(f"📝 OCR: {'ON' if self.ocr_enabled else 'OFF'}")
    
    def toggle_vcam(self):
        """Toggle virtual camera"""
        if not VIRTUAL_CAM_AVAILABLE:
            print("❌ Virtual camera not available")
            return
        
        if self.vcam_enabled:
            self.vcam.stop()
            self.vcam_enabled = False
        else:
            if self.vcam.start():
                self.vcam_enabled = True
    
    def toggle_preview(self):
        """Toggle preview"""
        self.show_preview = not self.show_preview
        if not self.show_preview:
            import cv2
            cv2.destroyAllWindows()
    
    def stop(self):
        """Stop application"""
        print("\n🛑 Stopping StreamBlur...")
        print(f"\n📊 Session Stats:")
        print(f"   Frames: {self.total_frames}")
        print(f"   Detections: {self.total_detections}")
        
        self.running = False
        
        if self.vcam_enabled:
            self.vcam.stop()
        
        self.capturer.cleanup()
        print("✅ StreamBlur stopped\n")


if __name__ == "__main__":
    # Create StreamBlur instance
    app = StreamBlurApp()
    
    # Create app runner
    runner = AppRunner(app)
    runner.start()
    
    # Create and run tray application
    from ui.tray_app import TrayApplication
    tray = TrayApplication(app)
    
    # Run Qt event loop
    sys.exit(tray.run())
