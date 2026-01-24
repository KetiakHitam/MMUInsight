"""Quick test to verify refactored moderation code works correctly"""

from moderation import ContentModerator

def test_case(text, should_block, test_name):
    result = ContentModerator.moderate(text)
    expected = not should_block
    passed = result.is_clean == expected
    status = "✓" if passed else "✗"
    print(f"{status} {test_name}: '{text}' -> {'BLOCKED' if not result.is_clean else 'CLEAN'}")
    if not passed:
        print(f"  Expected: {'CLEAN' if expected else 'BLOCKED'}, Got: {'CLEAN' if result.is_clean else 'BLOCKED'}")
        print(f"  Flags: {result.flags}")
    return passed

tests = [
    # Normal profanity
    ("fuck this professor", True, "Normal profanity"),
    ("This is shit teaching", True, "Normal profanity 2"),
    
    # Leetspeak
    ("f4ck this lecturer", True, "Leetspeak f4ck"),
    ("This is sh1t", True, "Leetspeak sh1t"),
    ("@sshole professor", True, "Leetspeak @ss"),
    
    # Misspellings
    ("fuk this class", True, "Misspelling fuk"),
    ("shyt professor", True, "Misspelling shyt"),
    ("biotch lecturer", True, "Misspelling biotch"),
    
    # Vowel removal
    ("fck this class", True, "Vowel removal fck"),
    ("btch lecturer", True, "Vowel removal btch"),
    
    # Spaced
    ("f u c k this", True, "Spaced profanity"),
    
    # Clean content
    ("Great professor, very helpful", False, "Clean content"),
    ("Excellent teaching style", False, "Clean content 2"),
    ("Nice class materials", False, "Clean content 3"),
    
    # Edge cases
    ("The duck was interesting", False, "Duck not dick"),
    ("Glass materials helpful", False, "Glass not ass"),
    ("This class was great", False, "Class not ass"),
]

print("=" * 80)
print("REFACTORED MODERATION CODE - VALIDATION TESTS")
print("=" * 80)
print()

passed = 0
failed = 0

for text, should_block, name in tests:
    if test_case(text, should_block, name):
        passed += 1
    else:
        failed += 1
    print()

print("=" * 80)
print(f"RESULTS: {passed} passed, {failed} failed out of {passed + failed} tests")
print(f"Success rate: {(passed / (passed + failed) * 100):.1f}%")
print("=" * 80)

if failed == 0:
    print("\n✅ All tests passed! Refactored code is working correctly.")
    exit(0)
else:
    print(f"\n❌ {failed} test(s) failed. Please review.")
    exit(1)
