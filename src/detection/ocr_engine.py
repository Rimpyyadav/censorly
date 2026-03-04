"""
OCR Engine Module
Extracts text from screen captures using Tesseract
"""

import pytesseract
import cv2
import numpy as np
from typing import List, Dict

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
        Enhanced preprocessing for better OCR
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Adaptive thresholding (best for screen text)
        thresh1 = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )

        return thresh1

    def extract_text_simple(self, image) -> str:
        """
        Extract text only (no positions)
        """
        preprocessed = self.preprocess_image(image)
        text = pytesseract.image_to_string(preprocessed)
        return text.strip()

    def extract_text_with_boxes(self, image) -> List[Dict]:
        """
        Extract text with bounding boxes
        """
        preprocessed = self.preprocess_image(image)

        data = pytesseract.image_to_data(
            preprocessed,
            output_type=pytesseract.Output.DICT
        )

        results = []
        n_boxes = len(data['text'])

        for i in range(n_boxes):
            text = data['text'][i].strip()

            # Handle confidence safely (sometimes '-1')
            try:
                confidence = int(float(data['conf'][i]))
            except:
                confidence = 0

            if confidence > self.confidence_threshold and text:
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
        """
        if results is None:
            results = self.last_results

        output = image.copy()

        for result in results:
            x, y, w, h = result['bbox']
            text = result['text']
            conf = result['confidence']

            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)

            label = f"{text[:20]} ({conf}%)"
            cv2.putText(
                output,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1
            )

        return output

    def get_all_text(self, results=None) -> str:
        """
        Get all detected text as single string
        """
        if results is None:
            results = self.last_results

        return " ".join(r['text'] for r in results)