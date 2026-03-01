"""
Pattern Matcher Module
Detects sensitive information using regex patterns
"""

import re
from typing import List, Dict, Tuple


class PatternMatcher:
    """Detects sensitive patterns in text"""
    
    # Regex patterns for sensitive information
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'api_key': r'\b[A-Za-z0-9_-]{32,}\b',
    }
    
    def __init__(self, enabled_patterns=None):
        """
        Initialize pattern matcher
        
        Args:
            enabled_patterns: List of pattern names to detect
                            (None = all patterns)
        """
        if enabled_patterns is None:
            self.enabled_patterns = list(self.PATTERNS.keys())
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
                    # Remove duplicates
                    matches = list(set(matches))
                    results[pattern_name] = matches
        
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