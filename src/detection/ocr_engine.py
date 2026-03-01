"""
OCR Engine Module
Extracts text from screen captures using Tesseract
"""

import pytesseract
import cv2
import numpy as np
from typing import List, Tuple, Dict

# Set tesseract path (adjust if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCREngine:
    """Handles OCR text extraction"""
    
    def __init__(self, confidence_threshold=60):
        """
        Initialize OCR engine
        
        Args:
            confidence_threshold: Minimum confidence to accept text (0-100)
        """
        self.confidence_threshold = confidence_threshold
        self.last_results = []
        
        # Test if Tesseract is available
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract OCR initialized")
        except Exception as e:
            print(f"❌ Tesseract not found: {e}")
            raise
    
    def preprocess_image(self, image):
        """
        Preprocess image for better OCR results
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Preprocessed grayscale image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to get black text on white background
        _, thresh = cv2.threshold(gray, 0, 255, 
                                  cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh
    
    def extract_text_simple(self, image) -> str:
        """
        Extract text only (no positions)
        
        Args:
            image: Input image
            
        Returns:
            Extracted text as string
        """
        preprocessed = self.preprocess_image(image)
        text = pytesseract.image_to_string(preprocessed)
        return text.strip()
    
    def extract_text_with_boxes(self, image) -> List[Dict]:
        """
        Extract text with bounding boxes
        
        Args:
            image: Input image
            
        Returns:
            List of dicts with 'text', 'bbox', 'confidence'
        """
        preprocessed = self.preprocess_image(image)
        
        # Get detailed data
        data = pytesseract.image_to_data(preprocessed, 
                                         output_type=pytesseract.Output.DICT)
        
        results = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            # Get confidence and text
            confidence = int(data['conf'][i])
            text = data['text'][i].strip()
            
            # Filter by confidence and empty text
            if confidence > self.confidence_threshold and text:
                # Get bounding box
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                
                results.append({
                    'text': text,
                    'bbox': (x, y, w, h),
                    'confidence': confidence
                })
        
        self.last_results = results
        return results
    
    def draw_boxes(self, image, results=None):
        """
        Draw bounding boxes on image
        
        Args:
            image: Image to draw on
            results: OCR results (if None, uses last results)
            
        Returns:
            Image with boxes drawn
        """
        if results is None:
            results = self.last_results
        
        output = image.copy()
        
        for result in results:
            x, y, w, h = result['bbox']
            text = result['text']
            conf = result['confidence']
            
            # Draw rectangle
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw text label
            label = f"{text[:20]} ({conf}%)"
            cv2.putText(output, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return output
    
    def get_all_text(self, results=None) -> str:
        """
        Get all detected text as single string
        
        Args:
            results: OCR results (if None, uses last results)
            
        Returns:
            Combined text string
        """
        if results is None:
            results = self.last_results
        
        texts = [r['text'] for r in results]
        return ' '.join(texts)