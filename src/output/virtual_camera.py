"""
Virtual Camera Output
Sends processed frames to virtual camera device
"""

import pyvirtualcam
import numpy as np
import cv2


class VirtualCamera:
    """Manages virtual camera output"""
    
    def __init__(self, width=1920, height=1080, fps=30):
        """
        Initialize virtual camera
        
        Args:
            width: Output width
            height: Output height
            fps: Output FPS
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.camera = None
        self.enabled = False
        
        print(f"🎥 Virtual Camera configured: {width}x{height} @ {fps}fps")
    
    def start(self):
        """Start virtual camera"""
        try:
            self.camera = pyvirtualcam.Camera(
                width=self.width,
                height=self.height,
                fps=self.fps,
                fmt=pyvirtualcam.PixelFormat.BGR
            )
            
            self.enabled = True
            print(f"✅ Virtual Camera started: {self.camera.device}")
            print(f"   Use this in OBS/Zoom: '{self.camera.device}'")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start virtual camera: {e}")
            print("   Make sure OBS Virtual Camera is installed")
            self.enabled = False
            return False
    
    def send_frame(self, frame):
        """
        Send frame to virtual camera
        
        Args:
            frame: Frame to send (BGR format)
        """
        if not self.enabled or self.camera is None:
            return
        
        try:
            # Resize if needed
            if frame.shape[1] != self.width or frame.shape[0] != self.height:
                frame = cv2.resize(frame, (self.width, self.height))
            
            # Ensure BGR format
            if frame.shape[2] == 4:  # BGRA
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            # Send to camera
            self.camera.send(frame)
            
        except Exception as e:
            print(f"⚠️ Error sending frame: {e}")
    
    def stop(self):
        """Stop virtual camera"""
        if self.camera:
            self.camera.close()
            self.enabled = False
            print("🛑 Virtual Camera stopped")
    
    def is_running(self):
        """Check if camera is running"""
        return self.enabled


class VirtualCameraFallback:
    """Fallback if pyvirtualcam not available"""
    
    def __init__(self, width, height, fps):
        print("⚠️ Virtual camera not available")
        self.enabled = False
    
    def start(self):
        return False
    
    def send_frame(self, frame):
        pass
    
    def stop(self):
        pass
    
    def is_running(self):
        return False