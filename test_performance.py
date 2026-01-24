"""Quick performance summary of refactored code"""
from moderation import ContentModerator
import time

# Test cases
tests = {
    'profanity': ['fuck', 'shit', 'ass', 'bitch', 'dick'],
    'leetspeak': ['f4ck', 'sh1t', '@ss', 'b!tch'],
    'misspellings': ['fuk', 'shyt', 'azz', 'biotch'],
    'vowel_removal': ['fck', 'sht', 'btch'],
    'spaced': ['f u c k', 's h i t'],
    'clean': ['great professor', 'excellent teaching', 'helpful class', 'nice lecturer']
}

print("="*60)
print("REFACTORED MODERATION - PERFORMANCE SUMMARY")
print("="*60)

total_tests = 0
passed_tests = 0
start_time = time.perf_counter()

for category, cases in tests.items():
    should_block = (category != 'clean')
    category_passed = 0
    
    for text in cases:
        result = ContentModerator.moderate(f"{text} professor teaching")
        is_blocked = not result.is_clean
        
        if is_blocked == should_block:
            category_passed += 1
            passed_tests += 1
        
        total_tests += 1
    
    print(f"{category:15} {category_passed}/{len(cases)} passed")

end_time = time.perf_counter()
elapsed = (end_time - start_time) * 1000

print("="*60)
print(f"TOTAL: {passed_tests}/{total_tests} passed ({passed_tests/total_tests*100:.1f}%)")
print(f"Time: {elapsed:.2f}ms ({elapsed/total_tests:.2f}ms per test)")
print("="*60)

if passed_tests == total_tests:
    print("\nSUCCESS: All refactored functionality working correctly!")
    print("\nOptimizations Applied:")
    print("  - Pre-compiled regex patterns (5+ patterns)")
    print("  - str.translate() instead of 13 str.replace() calls")
    print("  - Set for profanity deduplication (O(1) vs O(n))")
    print("  - Removed redundant 'not in' checks in loops")
    print("  - Cached vowels as frozenset")
    print("  - Walrus operator in list comprehensions")
    print("  - Eliminated unused LEETSPEAK_MAP (40+ lines)")
