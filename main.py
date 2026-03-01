"""
StreamBlur - Main Application
Real-time screen capture with OCR and pattern detection
"""

import cv2
import sys
import time

# Add src to path
sys.path.insert(0, 'src')

from capture.screen_capture import ScreenCapture
from detection.ocr_engine import OCREngine
from detection.pattern_matcher import PatternMatcher


class StreamBlur:
    """Main application class"""
    
    def __init__(self):
        # Initialize components
        print("\n🚀 Initializing StreamBlur...")
        print("━" * 50)
        
        self.capturer = ScreenCapture(monitor_index=1, target_fps=30)
        self.ocr = OCREngine(confidence_threshold=60)
        self.pattern_matcher = PatternMatcher(
            enabled_patterns=['email', 'phone', 'credit_card']
        )
        
        # Settings
        self.blur_enabled = False
        self.ocr_enabled = False
        self.show_text_boxes = False
        self.running = False
        
        # OCR optimization
        self.frame_count = 0
        self.ocr_interval = 5  # Run OCR every 5 frames
        self.last_ocr_results = []
        self.detected_sensitive = []
        
        print("\n✅ StreamBlur Ready!")
        print("━" * 50)
        print("Controls:")
        print("  B - Toggle blur ON/OFF")
        print("  O - Toggle OCR ON/OFF")
        print("  T - Toggle text boxes display")
        print("  Q - Quit application")
        print("━" * 50 + "\n")
    
    def apply_blur(self, frame):
        """Apply Gaussian blur to frame"""
        return cv2.GaussianBlur(frame, (21, 21), 0)
    
    def process_ocr(self, frame):
        """Run OCR and detect sensitive info"""
        # Extract text with positions
        results = self.ocr.extract_text_with_boxes(frame)
        self.last_ocr_results = results
        
        # Get all text
        all_text = self.ocr.get_all_text(results)
        
        # Find sensitive patterns
        patterns = self.pattern_matcher.find_patterns(all_text)
        
        # Store detected sensitive info
        self.detected_sensitive = []
        for pattern_type, matches in patterns.items():
            for match in matches:
                self.detected_sensitive.append({
                    'type': pattern_type,
                    'text': match
                })
        
        # Print detections
        if self.detected_sensitive:
            print(f"\n⚠️  Sensitive info detected:")
            for item in self.detected_sensitive:
                print(f"   {item['type']}: {item['text']}")
    
    def add_overlay(self, frame):
        """Add status overlay to frame"""
        y_pos = 30
        
        # FPS
        cv2.putText(frame, f'FPS: {self.capturer.get_fps():.1f}', 
                    (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, (0, 255, 0), 2)
        y_pos += 35
        
        # Blur status
        blur_text = "BLUR: ON" if self.blur_enabled else "BLUR: OFF"
        blur_color = (0, 255, 0) if self.blur_enabled else (0, 0, 255)
        cv2.putText(frame, blur_text, (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, blur_color, 2)
        y_pos += 35
        
        # OCR status
        ocr_text = "OCR: ON" if self.ocr_enabled else "OCR: OFF"
        ocr_color = (0, 255, 0) if self.ocr_enabled else (128, 128, 128)
        cv2.putText(frame, ocr_text, (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, ocr_color, 2)
        y_pos += 35
        
        # Sensitive info count
        if self.ocr_enabled and self.detected_sensitive:
            count_text = f"⚠️ Sensitive: {len(self.detected_sensitive)}"
            cv2.putText(frame, count_text, (10, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            y_pos += 35
        
        # Instructions
        cv2.putText(frame, "B=Blur | O=OCR | T=Boxes | Q=Quit", 
                    (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.5, (255, 255, 255), 1)
        
        return frame
    
    def run(self):
        """Main application loop"""
        self.running = True
        
        try:
            while self.running:
                # Capture frame
                frame = self.capturer.capture_frame()
                
                # Run OCR periodically
                if self.ocr_enabled:
                    self.frame_count += 1
                    if self.frame_count >= self.ocr_interval:
                        self.process_ocr(frame)
                        self.frame_count = 0
                
                # Show text boxes if enabled
                if self.show_text_boxes and self.last_ocr_results:
                    frame = self.ocr.draw_boxes(frame, self.last_ocr_results)
                
                # Apply blur if enabled
                if self.blur_enabled:
                    frame = self.apply_blur(frame)
                
                # Add overlay
                frame = self.add_overlay(frame)
                
                # Display
                cv2.imshow('StreamBlur - Day 3-4', frame)
                
                # Handle input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.stop()
                elif key == ord('b'):
                    self.toggle_blur()
                elif key == ord('o'):
                    self.toggle_ocr()
                elif key == ord('t'):
                    self.toggle_text_boxes()
        
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.stop()
    
    def toggle_blur(self):
        """Toggle blur on/off"""
        self.blur_enabled = not self.blur_enabled
        status = "ON" if self.blur_enabled else "OFF"
        print(f"🔵 Blur: {status}")
    
    def toggle_ocr(self):
        """Toggle OCR on/off"""
        self.ocr_enabled = not self.ocr_enabled
        status = "ON" if self.ocr_enabled else "OFF"
        print(f"📝 OCR: {status}")
    
    def toggle_text_boxes(self):
        """Toggle text box display"""
        self.show_text_boxes = not self.show_text_boxes
        status = "ON" if self.show_text_boxes else "OFF"
        print(f"📦 Text Boxes: {status}")
    
    def stop(self):
        """Stop application"""
        print("\n🛑 Stopping StreamBlur...")
        self.running = False
        cv2.destroyAllWindows()
        self.capturer.cleanup()
        print("✅ Done!\n")


if __name__ == "__main__":
    app = StreamBlur()
    app.run()
