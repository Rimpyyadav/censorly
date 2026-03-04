"""
Pattern Matcher Module - Enhanced
"""

import re
from typing import List, Dict, Tuple


class PatternMatcher:
    """Detects sensitive patterns in text"""
    
    # Enhanced regex patterns
    PATTERNS = {
        # Email - more permissive
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        
        # Phone - multiple formats
        'phone': r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        
        # Credit card - with or without spaces/dashes
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        
        # SSN
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        
        # IP Address
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        
        # API Keys (long alphanumeric strings)
        'api_key': r'\b[A-Za-z0-9_-]{32,}\b',
        
        # NEW: Any sequence that looks like a password/key
        'secret_key': r'\b[A-Za-z0-9!@#$%^&*()_+\-=]{16,}\b',
        
        # NEW: Credit card CVV
        'cvv': r'\b\d{3,4}\b',
        
        # NEW: Dates that might be sensitive (DOB)
        'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        
        # NEW: Account numbers
        'account_number': r'\b\d{8,17}\b',
        
        # NEW: Zip codes
        'zip_code': r'\b\d{5}(-\d{4})?\b',
    }
    
    def __init__(self, enabled_patterns=None):
        """
        Initialize pattern matcher
        
        Args:
            enabled_patterns: List of pattern names to detect
                            (None = all patterns)
        """
        if enabled_patterns is None:
            # Enable most common patterns by default
            self.enabled_patterns = [
                'email', 'phone', 'credit_card', 'ssn', 
                'ip_address', 'api_key', 'account_number'
            ]
        else:
            self.enabled_patterns = enabled_patterns
        
        print(f"✅ Pattern Matcher initialized")
        print(f"   Detecting: {', '.join(self.enabled_patterns)}")
    
    def find_patterns(self, text: str) -> Dict[str, List[str]]:
        """
        Find all patterns in text
        
        Args:
            text: Text to search
            
        Returns:
            Dict mapping pattern_name -> list of matches
        """
        results = {}
        
        for pattern_name in self.enabled_patterns:
            if pattern_name in self.PATTERNS:
                regex = self.PATTERNS[pattern_name]
                matches = re.findall(regex, text, re.IGNORECASE)
                
                if matches:
                    # Clean up tuples from regex groups
                    clean_matches = []
                    for match in matches:
                        if isinstance(match, tuple):
                            # Take the full match
                            match = ''.join(match)
                        clean_matches.append(match)
                    
                    # Remove duplicates
                    clean_matches = list(set(clean_matches))
                    results[pattern_name] = clean_matches
        
        return results
    
    def find_pattern_positions(self, text: str, pattern_name: str) -> List[Tuple[str, int, int]]:
        """
        Find pattern matches with their positions
        
        Args:
            text: Text to search
            pattern_name: Name of pattern to find
            
        Returns:
            List of tuples (matched_text, start_pos, end_pos)
        """
        if pattern_name not in self.PATTERNS:
            return []
        
        regex = self.PATTERNS[pattern_name]
        matches = []
        
        for match in re.finditer(regex, text, re.IGNORECASE):
            matches.append((
                match.group(),
                match.start(),
                match.end()
            ))
        
        return matches
    
    def is_sensitive(self, text: str) -> bool:
        """
        Check if text contains any sensitive information
        
        Args:
            text: Text to check
            
        Returns:
            True if sensitive info found
        """
        # Quick check for common patterns first
        if '@' in text:  # Likely email
            return True
        
        # Check if it's mostly numbers (could be phone/card/account)
        digit_ratio = sum(c.isdigit() for c in text) / max(len(text), 1)
        if digit_ratio > 0.5 and len(text) >= 8:
            return True
        
        # Full pattern check
        results = self.find_patterns(text)
        return len(results) > 0
    
    def add_custom_pattern(self, name: str, regex: str):
        """
        Add custom pattern
        
        Args:
            name: Pattern name
            regex: Regular expression
        """
        self.PATTERNS[name] = regex
        if name not in self.enabled_patterns:
            self.enabled_patterns.append(name)
        
        print(f"✅ Added custom pattern: {name}")