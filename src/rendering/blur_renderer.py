"""
Blur Renderer Module
Applies blur to specific regions of the frame
"""

import cv2
import numpy as np
from typing import List, Tuple


class BlurRenderer:
    """Handles selective blur rendering"""
    
    def __init__(self, blur_strength=5):
        """
        Initialize blur renderer
        
        Args:
            blur_strength: Blur intensity (1-10)
        """
        self.blur_strength = blur_strength
        self.kernel_size = self._calculate_kernel_size(blur_strength)
        
        print(f"✅ Blur Renderer initialized (strength: {blur_strength})")
    
    def _calculate_kernel_size(self, strength: int) -> Tuple[int, int]:
        """
        Calculate kernel size from strength
        
        Args:
            strength: Blur strength (1-10)
            
        Returns:
            Tuple of (width, height) for kernel (must be odd numbers)
        """
        # Map strength 1-10 to kernel size 5-35
        size = max(5, strength * 3 + 2)
        
        # Ensure odd number
        if size % 2 == 0:
            size += 1
        
        return (size, size)
    
    def blur_full_frame(self, frame):
        """
        Apply blur to entire frame
        
        Args:
            frame: Input frame
            
        Returns:
            Blurred frame
        """
        return cv2.GaussianBlur(frame, self.kernel_size, 0)
    
    def blur_regions(self, frame, regions: List[Tuple[int, int, int, int]]):
        """
        Apply blur to specific regions only
        
        Args:
            frame: Input frame
            regions: List of (x, y, w, h) tuples
            
        Returns:
            Frame with blurred regions
        """
        output = frame.copy()
        
        for region in regions:
            x, y, w, h = region
            
            # Ensure coordinates are within frame bounds
            x = max(0, x)
            y = max(0, y)
            w = min(w, frame.shape[1] - x)
            h = min(h, frame.shape[0] - y)
            
            # Skip invalid regions
            if w <= 0 or h <= 0:
                continue
            
            # Extract region
            roi = output[y:y+h, x:x+w]
            
            # Apply blur
            blurred_roi = cv2.GaussianBlur(roi, self.kernel_size, 0)
            
            # Put back
            output[y:y+h, x:x+w] = blurred_roi
        
        return output
    
    def blur_regions_with_padding(self, frame, regions: List[Tuple[int, int, int, int]], 
                                   padding: int = 10):
        """
        Blur regions with extra padding around them
        
        Args:
            frame: Input frame
            regions: List of (x, y, w, h) tuples
            padding: Extra pixels to blur around region
            
        Returns:
            Frame with blurred regions
        """
        padded_regions = []
        
        for region in regions:
            x, y, w, h = region
            
            # Add padding
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(w + padding * 2, frame.shape[1] - x)
            h = min(h + padding * 2, frame.shape[0] - y)
            
            padded_regions.append((x, y, w, h))
        
        return self.blur_regions(frame, padded_regions)
    
    def draw_blur_indicators(self, frame, regions: List[Tuple[int, int, int, int]]):
        """
        Draw red borders around regions that will be blurred
        
        Args:
            frame: Input frame
            regions: List of (x, y, w, h) tuples
            
        Returns:
            Frame with indicators drawn
        """
        output = frame.copy()
        
        for region in regions:
            x, y, w, h = region
            
            # Draw red rectangle
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            # Add "BLUR" label
            cv2.putText(output, "BLUR", (x, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        return output
    
    def set_blur_strength(self, strength: int):
        """
        Update blur strength
        
        Args:
            strength: New blur strength (1-10)
        """
        self.blur_strength = max(1, min(10, strength))
        self.kernel_size = self._calculate_kernel_size(self.blur_strength)
        print(f"🔧 Blur strength: {self.blur_strength}")