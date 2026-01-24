"""
Test script for the moderation system
Run this to test how the moderation system catches violations
"""

from moderation import ContentModerator, get_moderation_summary

def print_result(test_name, text, result):
    """Pretty print a moderation result"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Text: {text[:80]}{'...' if len(text) > 80 else ''}")
    print(f"Clean: {result.is_clean}")
    print(f"Severity: {result.severity}")
    print(f"Flags: {result.flags}")
    print(f"Summary: {get_moderation_summary(result.flags)}")
    print()

# Test 1: Clean review - SHOULD PASS
print("\n" + "█"*60)
print("✓ CLEAN CONTENT (Should Pass)")
print("█"*60)
clean_text = "This professor is amazing! Very clear explanations, engaging lectures, and always responds to emails. Highly recommend!"
result = ContentModerator.moderate(clean_text)
print_result("Clean Review", clean_text, result)

# Test 2: Profanity - SHOULD FAIL
print("\n" + "█"*60)
print("✗ PROFANITY (Should Fail)")
print("█"*60)
profane = "This fucking shit professor is a bastard! Worst lecturer ever."
result = ContentModerator.moderate(profane)
print_result("Profanity Test", profane, result)

# Test 3: Too short - SHOULD FAIL
print("\n" + "█"*60)
print("✗ TOO SHORT (Should Fail)")
print("█"*60)
short = "Bad prof"
result = ContentModerator.moderate(short)
print_result("Too Short Test", short, result)

# Test 4: Excessive caps - SHOULD FAIL
print("\n" + "█"*60)
print("✗ EXCESSIVE CAPS (Should Fail)")
print("█"*60)
caps = "THIS LECTURER IS ABSOLUTELY TERRIBLE! THE WORST PROFESSOR I'VE EVER HAD!"
result = ContentModerator.moderate(caps)
print_result("Caps Lock Abuse", caps, result)

# Test 5: Repeated characters - SHOULD FAIL
print("\n" + "█"*60)
print("✗ REPEATED CHARACTERS (Should Fail)")
print("█"*60)
repeated_chars = "This professor is sooooooo bad and I hate theeeeeee lectures"
result = ContentModerator.moderate(repeated_chars)
print_result("Repeated Characters", repeated_chars, result)

# Test 6: Word repetition - SHOULD FAIL
print("\n" + "█"*60)
print("✗ WORD REPETITION (Should Fail)")
print("█"*60)
repeated_words = "Bad bad bad bad bad bad bad lecture. Terrible terrible terrible terrible terrible terrible"
result = ContentModerator.moderate(repeated_words)
print_result("Word Repetition", repeated_words, result)

# Test 7: Too many links - SHOULD FAIL
print("\n" + "█"*60)
print("✗ SPAM LINKS (Should Fail)")
print("█"*60)
spam_links = "Check this out http://spam1.com and http://spam2.com and http://spam3.com for more info"
result = ContentModerator.moderate(spam_links)
print_result("Excessive Links", spam_links, result)

# Test 8: Too long - SHOULD FAIL
print("\n" + "█"*60)
print("✗ TOO LONG (Should Fail)")
print("█"*60)
long_text = "a" * 5001
result = ContentModerator.moderate(long_text)
print_result("Too Long Text", long_text, result)

# Test 9: Gibberish - SHOULD FAIL
print("\n" + "█"*60)
print("✗ GIBBERISH (Should Fail)")
print("█"*60)
gibberish = "qwerty asdfgh zxcvbn mnbvcx lkjhgf poiuyt This is keyboard mashing"
result = ContentModerator.moderate(gibberish)
print_result("Gibberish Text", gibberish, result)

# Test 10: Borderline - Mix of issues
print("\n" + "█"*60)
print("⚠ BORDERLINE (May have issues)")
print("█"*60)
borderline = "Ok ok ok ok ok ok professor but not the best best best best"
result = ContentModerator.moderate(borderline)
print_result("Borderline Content", borderline, result)

print("\n" + "="*60)
print("TESTING COMPLETE")
print("="*60)
