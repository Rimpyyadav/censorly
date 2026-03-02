"""
Application Runner - Fixed recursion
"""

import threading
import time
import mss
import numpy as np


class AppRunner:
    """Runs StreamBlur in background thread"""
    
    def __init__(self, streamblur_app):
        self.streamblur = streamblur_app
        self.thread = None
        self.running = False
        self.preview_window_name = 'StreamBlur - Preview'
    
    def start(self):
        """Start processing thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print("✅ Processing thread started")
    
    def _run_loop(self):
        """Main processing loop"""
        import cv2
        
        # Create screen capture for this thread
        sct = mss.mss()
        monitor = sct.monitors[1]
        
        fps = 0
        frame_count = 0
        fps_start = time.time()
        
        # Position preview window off to the side initially
        preview_positioned = False
        
        try:
            while self.running and self.streamblur.running:
                # Capture
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Update FPS
                frame_count += 1
                elapsed = time.time() - fps_start
                if elapsed > 1:
                    fps = frame_count / elapsed
                    self.streamblur.capturer.fps = fps
                    frame_count = 0
                    fps_start = time.time()
                
                self.streamblur.total_frames += 1
                
                # Detection
                if self.streamblur.ocr_enabled:
                    self.streamblur.frame_count += 1
                    if self.streamblur.frame_count >= self.streamblur.ocr_interval:
                        self.streamblur.process_detection(frame)
                        self.streamblur.frame_count = 0
                
                # Detection boxes
                if self.streamblur.show_detection_boxes:
                    frame = self.streamblur.detector.draw_detection_boxes(frame)
                
                # Blur
                output_frame = self.streamblur.render_frame(frame)
                
                # Overlay
                display_frame = self.streamblur.add_overlay(output_frame.copy())
                
                # Virtual camera
                if self.streamblur.vcam_enabled:
                    self.streamblur.vcam.send_frame(output_frame)
                
                # Preview (with TOPMOST flag to prevent recursion)
                if self.streamblur.show_preview:
                    cv2.imshow(self.preview_window_name, display_frame)
                    
                    # Position window only once
                    if not preview_positioned:
                        cv2.setWindowProperty(self.preview_window_name, 
                                            cv2.WND_PROP_TOPMOST, 1)
                        # Move to top-right corner
                        cv2.moveWindow(self.preview_window_name, 
                                      monitor['width'] - 640, 0)
                        preview_positioned = True
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        self.stop()
                        break
                
                # Small delay
                time.sleep(0.001)
        
        except Exception as e:
            print(f"❌ Error in processing thread: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            sct.close()
            cv2.destroyAllWindows()
            print("🧹 Thread cleanup complete")
    
    def stop(self):
        """Stop processing thread"""
        print("🛑 Stopping processing thread...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        print("✅ Thread stopped")