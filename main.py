"""
StreamBlur - Main Application
Day 7-8: Virtual Camera Integration
"""

import cv2
import sys
import time

# Add src to path
sys.path.insert(0, 'src')

from capture.screen_capture import ScreenCapture
from detection.detection_manager import DetectionManager
from rendering.blur_renderer import BlurRenderer

# Try to import virtual camera
try:
    from output.virtual_camera import VirtualCamera
    VIRTUAL_CAM_AVAILABLE = True
except ImportError:
    from output.virtual_camera import VirtualCameraFallback as VirtualCamera
    VIRTUAL_CAM_AVAILABLE = False


class StreamBlur:
    """Main application class - FINAL VERSION"""
    
    def __init__(self):
        # Initialize components
        print("\n🚀 Initializing StreamBlur v0.4...")
        print("━" * 60)
        
        self.capturer = ScreenCapture(monitor_index=1, target_fps=30)
        self.detector = DetectionManager()
        self.renderer = BlurRenderer(blur_strength=7)
        
        # Virtual camera
        width, height = self.capturer.get_resolution()
        self.vcam = VirtualCamera(width=width, height=height, fps=30)
        
        # Settings
        self.blur_mode = "none"  # none, full, regions
        self.ocr_enabled = False
        self.vcam_enabled = False
        self.show_detection_boxes = False
        self.show_preview = True
        self.running = False
        
        # Performance
        self.frame_count = 0
        self.ocr_interval = 5
        self.sensitive_regions = []
        
        # Stats
        self.total_frames = 0
        self.total_detections = 0
        
        print("\n✅ StreamBlur Ready!")
        print("━" * 60)
        print("Controls:")
        print("  1 - Blur: OFF")
        print("  2 - Blur: FULL SCREEN")
        print("  3 - Blur: REGIONS ONLY (smart) ⭐")
        print("  O - Toggle OCR detection")
        print("  V - Toggle Virtual Camera output")
        print("  D - Toggle detection boxes")
        print("  P - Toggle preview window")
        print("  + - Increase blur strength")
        print("  - - Decrease blur strength")
        print("  Q - Quit")
        print("━" * 60 + "\n")
    
    def process_detection(self, frame):
        """Run detection"""
        self.sensitive_regions = self.detector.detect_sensitive_regions(frame)
        
        if self.sensitive_regions:
            self.total_detections += len(self.sensitive_regions)
            
            # Print first time only
            detections = self.detector.get_last_detections()
            print(f"\n⚠️  Detected {len(detections)} sensitive item(s)")
    
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
        """Add status overlay"""
        y_pos = 30
        
        # FPS
        cv2.putText(frame, f'FPS: {self.capturer.get_fps():.1f}', 
                    (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, (0, 255, 0), 2)
        y_pos += 35
        
        # Blur mode
        blur_text = f"Blur: {self.blur_mode.upper()}"
        blur_colors = {
            "none": (128, 128, 128),
            "full": (255, 165, 0),
            "regions": (0, 255, 0)
        }
        cv2.putText(frame, blur_text, (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                    blur_colors.get(self.blur_mode, (255, 255, 255)), 2)
        y_pos += 35
        
        # OCR status
        ocr_text = f"OCR: {'ON' if self.ocr_enabled else 'OFF'}"
        cv2.putText(frame, ocr_text, (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                    (0, 255, 0) if self.ocr_enabled else (128, 128, 128), 2)
        y_pos += 35
        
        # Virtual camera status
        vcam_text = f"VCam: {'ON' if self.vcam_enabled else 'OFF'}"
        cv2.putText(frame, vcam_text, (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0) if self.vcam_enabled else (128, 128, 128), 2)
        y_pos += 35
        
        # Sensitive regions
        if self.sensitive_regions:
            cv2.putText(frame, f"⚠️ Blurred: {len(self.sensitive_regions)}", 
                        (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (0, 165, 255), 2)
            y_pos += 35
        
        # Blur strength
        cv2.putText(frame, f"Strength: {self.renderer.blur_strength}/10", 
                    (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, (255, 255, 255), 1)
        y_pos += 30
        
        # Stats
        cv2.putText(frame, f"Frames: {self.total_frames} | Detections: {self.total_detections}", 
                    (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.5, (200, 200, 200), 1)
        
        return frame
    
    def run(self):
        """Main loop"""
        self.running = True
        
        try:
            while self.running:
                # Capture
                frame = self.capturer.capture_frame()
                self.total_frames += 1
                
                # Detection
                if self.ocr_enabled:
                    self.frame_count += 1
                    if self.frame_count >= self.ocr_interval:
                        self.process_detection(frame)
                        self.frame_count = 0
                
                # Show detection boxes BEFORE blur
                if self.show_detection_boxes:
                    frame = self.detector.draw_detection_boxes(frame)
                
                # Apply blur
                output_frame = self.render_frame(frame)
                
                # Add overlay
                display_frame = self.add_overlay(output_frame.copy())
                
                # Send to virtual camera (without overlay)
                if self.vcam_enabled:
                    self.vcam.send_frame(output_frame)
                
                # Show preview
                if self.show_preview:
                    cv2.imshow('StreamBlur - Preview', display_frame)
                
                # Handle input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    self.stop()
                elif key == ord('1'):
                    self.set_blur_mode("none")
                elif key == ord('2'):
                    self.set_blur_mode("full")
                elif key == ord('3'):
                    self.set_blur_mode("regions")
                elif key == ord('o'):
                    self.toggle_ocr()
                elif key == ord('v'):
                    self.toggle_vcam()
                elif key == ord('d'):
                    self.show_detection_boxes = not self.show_detection_boxes
                elif key == ord('p'):
                    self.toggle_preview()
                elif key == ord('+') or key == ord('='):
                    self.renderer.set_blur_strength(self.renderer.blur_strength + 1)
                elif key == ord('-') or key == ord('_'):
                    self.renderer.set_blur_strength(self.renderer.blur_strength - 1)
        
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self.stop()
    
    def set_blur_mode(self, mode: str):
        """Set blur mode"""
        self.blur_mode = mode
        print(f"\n🔵 Blur Mode: {mode.upper()}")
    
    def toggle_ocr(self):
        """Toggle OCR"""
        self.ocr_enabled = not self.ocr_enabled
        if not self.ocr_enabled:
            self.sensitive_regions = []
        print(f"\n📝 OCR: {'ON' if self.ocr_enabled else 'OFF'}")
    
    def toggle_vcam(self):
        """Toggle virtual camera"""
        if not VIRTUAL_CAM_AVAILABLE:
            print("\n❌ Virtual camera not available")
            print("   Install: pip install pyvirtualcam")
            return
        
        if self.vcam_enabled:
            self.vcam.stop()
            self.vcam_enabled = False
            print("\n📹 Virtual Camera: OFF")
        else:
            if self.vcam.start():
                self.vcam_enabled = True
                print("\n📹 Virtual Camera: ON")
                print(f"   Device: {self.vcam.camera.device}")
    
    def toggle_preview(self):
        """Toggle preview window"""
        self.show_preview = not self.show_preview
        if not self.show_preview:
            cv2.destroyAllWindows()
        print(f"\n🖼️  Preview: {'ON' if self.show_preview else 'OFF'}")
    
    def stop(self):
        """Stop application"""
        print("\n🛑 Stopping StreamBlur...")
        print(f"\n📊 Session Stats:")
        print(f"   Total Frames: {self.total_frames}")
        print(f"   Total Detections: {self.total_detections}")
        
        self.running = False
        
        if self.vcam_enabled:
            self.vcam.stop()
        
        cv2.destroyAllWindows()
        self.capturer.cleanup()
        
        print("\n✅ StreamBlur stopped!\n")


if __name__ == "__main__":
    app = StreamBlur()
    app.run()
