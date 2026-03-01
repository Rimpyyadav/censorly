"""
Screen Capture Module
Handles real-time screen capture with performance monitoring
"""

import mss
import numpy as np
import cv2
import time


class ScreenCapture:
    """Captures screen in real-time"""
    
    def __init__(self, monitor_index=1, target_fps=30):
        """
        Initialize screen capture
        
        Args:
            monitor_index: Which monitor to capture (0=all, 1=primary)
            target_fps: Target frames per second
        """
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[monitor_index]
        self.target_fps = target_fps
        self.frame_delay = 1.0 / target_fps
        
        # FPS tracking
        self.fps = 0
        self.frame_count = 0
        self.fps_start_time = time.time()
        
        print(f"📺 Monitor: {self.monitor['width']}x{self.monitor['height']}")
        print(f"🎯 Target FPS: {target_fps}")
    
    def capture_frame(self):
        """
        Capture single frame from screen
        
        Returns:
            numpy.ndarray: Frame in BGR format
        """
        # Grab screenshot
        screenshot = self.sct.grab(self.monitor)
        
        # Convert to numpy array
        frame = np.array(screenshot)
        
        # Convert BGRA to BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        
        # Update FPS
        self._update_fps()
        
        return frame
    
    def _update_fps(self):
        """Update FPS counter"""
        self.frame_count += 1
        elapsed = time.time() - self.fps_start_time
        
        if elapsed > 1:  # Update every second
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.fps_start_time = time.time()
    
    def get_fps(self):
        """Get current FPS"""
        return self.fps
    
    def get_resolution(self):
        """Get monitor resolution"""
        return (self.monitor['width'], self.monitor['height'])
    
    def cleanup(self):
        """Cleanup resources"""
        self.sct.close()