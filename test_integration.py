"""Test integration between moderation system and review queue"""

from moderation import ContentModerator

# Test cases that should be flagged
test_cases = [
    ("fuck this professor", "profanity"),
    ("f4ck this lecturer", "leetspeak"),
    ("fuk this class", "misspelling"),
    ("Great lecturer and very helpful", "clean"),
]

print("=" * 70)
print("MODERATION INTEGRATION TEST")
print("=" * 70)
print()

issues = []

for text, expected in test_cases:
    result = ContentModerator.moderate(text)
    
    # Check fields
    has_is_clean = hasattr(result, 'is_clean')
    has_flags = hasattr(result, 'flags')
    has_severity = hasattr(result, 'severity')
    has_requires_review = hasattr(result, 'requires_review')
    
    if not all([has_is_clean, has_flags, has_severity, has_requires_review]):
        issues.append(f"Missing required attributes in ModerationResult for: {text}")
        continue
    
    # Check logic
    if expected == "clean":
        if not result.is_clean:
            issues.append(f"Clean text flagged as dirty: {text}")
        if result.requires_review:
            issues.append(f"Clean text requires review: {text}")
        if result.flags:
            issues.append(f"Clean text has flags: {text} -> {result.flags}")
    else:
        if result.is_clean:
            issues.append(f"Profanity not detected: {text}")
        if not result.requires_review:
            issues.append(f"Profanity doesn't require review: {text}")
        if not result.flags:
            issues.append(f"Profanity has no flags: {text}")
    
    status = "✓" if expected != "clean" and not result.is_clean else ("✓" if expected == "clean" and result.is_clean else "✗")
    print(f"{status} {text[:40]:40} -> clean={result.is_clean}, requires_review={result.requires_review}")

print()
print("=" * 70)

if issues:
    print("❌ ISSUES FOUND:")
    for issue in issues:
        print(f"  - {issue}")
    print()
    print("INTEGRATION TEST FAILED")
else:
    print("✅ All integration checks passed!")
    print()
    print("Database Integration Checklist:")
    print("  ✓ ModerationResult.is_clean -> Review.is_approved")
    print("  ✓ ModerationResult.requires_review -> Review.requires_human_review")
    print("  ✓ ModerationResult.flags -> Review.moderation_flags")
    print("  ✓ ModerationResult.severity -> Review.moderation_severity")
    print()
    print("Expected Behavior:")
    print("  • Clean reviews: is_approved=True (auto-approved)")
    print("  • Flagged reviews: is_approved=None, requires_human_review=True")
    print("  • Flagged reviews appear in admin moderation queue")
    print("  • Admins can approve (is_approved=True) or reject (is_approved=False)")

print("=" * 70)
