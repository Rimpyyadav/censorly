"""
Detection Manager
Coordinates OCR and pattern matching to find sensitive regions
"""

import cv2
from typing import List, Dict, Tuple
from .ocr_engine import OCREngine
from .pattern_matcher import PatternMatcher


class DetectionManager:
    """Manages detection of sensitive information"""
    
    def __init__(self):
        self.ocr = OCREngine(confidence_threshold=60)
        self.pattern_matcher = PatternMatcher(
            enabled_patterns=['email', 'phone', 'credit_card', 'ip_address']
        )
        
        # Cache
        self.last_ocr_results = []
        self.last_sensitive_regions = []
        self.last_detections = []
        
        print("✅ Detection Manager initialized")
    
    def detect_sensitive_regions(self, frame) -> List[Tuple[int, int, int, int]]:
        """
        Detect all sensitive regions in frame
        
        Args:
            frame: Input frame
            
        Returns:
            List of (x, y, w, h) regions to blur
        """
        # Run OCR
        ocr_results = self.ocr.extract_text_with_boxes(frame)
        self.last_ocr_results = ocr_results
        
        # Find sensitive regions
        sensitive_regions = []
        detections = []
        
        for result in ocr_results:
            text = result['text']
            bbox = result['bbox']
            
            # Check if text is sensitive
            if self.pattern_matcher.is_sensitive(text):
                sensitive_regions.append(bbox)
                
                # Find what pattern matched
                patterns = self.pattern_matcher.find_patterns(text)
                for pattern_type, matches in patterns.items():
                    for match in matches:
                        detections.append({
                            'type': pattern_type,
                            'text': match,
                            'bbox': bbox
                        })
        
        self.last_sensitive_regions = sensitive_regions
        self.last_detections = detections
        
        return sensitive_regions
    
    def get_last_detections(self) -> List[Dict]:
        """Get last detection results"""
        return self.last_detections
    
    def draw_detection_boxes(self, frame, show_all_text=False):
        """
        Draw boxes around detections
        
        Args:
            frame: Input frame
            show_all_text: Show all OCR text or only sensitive
            
        Returns:
            Frame with boxes drawn
        """
        output = frame.copy()
        
        if show_all_text:
            # Draw all OCR results in green
            for result in self.last_ocr_results:
                x, y, w, h = result['bbox']
                cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 1)
        
        # Draw sensitive regions in red
        for detection in self.last_detections:
            x, y, w, h = detection['bbox']
            
            # Red box
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            # Label
            label = f"{detection['type']}"
            cv2.putText(output, label, (x, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        return output