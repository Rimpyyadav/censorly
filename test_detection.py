"""
Test detection accuracy
"""

import sys
sys.path.insert(0, 'src')

from detection.pattern_matcher import PatternMatcher

# Test cases
test_texts = [
    "Email: john@example.com",
    "Phone: 555-123-4567",
    "Call me at (555) 123-4567",
    "Card: 4532-1234-5678-9010",
    "Account: 123456789",
    "IP: 192.168.1.1",
    "Password: MySecret123!",
    "123-45-6789",  # SSN
    "12345",  # Zip code
]

matcher = PatternMatcher()

print("🧪 Testing Pattern Detection\n")
print("=" * 60)

for text in test_texts:
    print(f"\nText: '{text}'")
    results = matcher.find_patterns(text)
    
    if results:
        print(f"✅ DETECTED:")
        for pattern_type, matches in results.items():
            print(f"   {pattern_type}: {matches}")
    else:
        print(f"❌ Nothing detected")

print("\n" + "=" * 60)
print("\n✅ Test complete!")