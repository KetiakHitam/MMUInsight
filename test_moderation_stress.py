"""
Stress test for moderation system - Finding vulnerabilities and bypass techniques
This simulates malicious users trying to harm lecturers or the website
"""

from moderation import ContentModerator, ModerationResult

def print_result(test_name: str, text: str, result: ModerationResult):
    """Print test results"""
    status = "✓ BLOCKED" if not result.is_clean else "✗ BYPASSED"
    print(f"\n{status} | {test_name}")
    print(f"Text: {text[:100]}...")
    print(f"Severity: {result.severity}")
    print(f"Flags: {result.flags}")
    print("-" * 80)

def run_stress_tests():
    """Run comprehensive bypass attempts"""
    
    print("=" * 80)
    print("MODERATION SYSTEM STRESS TEST - Attack Simulation")
    print("=" * 80)
    
    # === PROFANITY BYPASS ATTEMPTS ===
    print("\n\n### PROFANITY BYPASS ATTEMPTS ###\n")
    
    # Test 1: Leetspeak substitution
    tests = [
        ("Leetspeak: f4ck", "This lecturer is f4cking terrible and sh1t at teaching"),
        ("Leetspeak: @ss", "This @sshole is the worst lecturer ever seen"),
        ("Leetspeak: b!tch", "What a b!tch, she's such a terrible professor"),
        
        # Test 2: Character substitution with symbols
        ("Symbol substitution", "F*ck this lecturer, sh*t professor, @ss teacher"),
        ("Symbol substitution 2", "This f@ck!ng lecturer is cr@p at everything"),
        
        # Test 3: Homoglyphs (similar looking characters)
        ("Homoglyphs", "This fuсk is terrible"),  # Using Cyrillic 'с' instead of 'c'
        
        # Test 4: Unicode tricks
        ("Zero-width spaces", "f\u200Buck this terrible lecturer"),  # Zero-width space
        ("Invisible chars", "sh\u200Dit professor"),  # Zero-width joiner
        
        # Test 5: Backwards/reversed
        ("Reversed", "This lecturer is a kcuf terrible teacher, tihs professor"),
        
        # Test 6: Common misspellings
        ("Misspellings", "Fuk this lecturer, shyt professor, azz teacher, biotch"),
        ("Misspellings 2", "Phuck this terrible prof, shiit at teaching"),
        
        # Test 7: Mixed with numbers/symbols
        ("Number mixing", "F_U_C_K this lecturer is the sh!++est professor"),
        
        # Test 8: Spaced already (should be caught)
        ("Spaced profanity", "f u c k this terrible s h i t professor"),
        
        # Test 9: Word boundaries
        ("Word boundaries", "This pro-f-u-c-k-ing lecturer is terrible"),
        
        # Test 10: Camel case
        ("Camel case", "FuCk this lecturer, ShIt professor, aSs teacher"),
    ]
    
    for test_name, text in tests:
        result = ContentModerator.moderate(text)
        print_result(test_name, text, result)
    
    # === SPAM/MANIPULATION ATTEMPTS ===
    print("\n\n### SPAM & MANIPULATION ATTEMPTS ###\n")
    
    spam_tests = [
        # Test 11: Hidden links with URL shorteners
        ("URL shorteners", "Great prof! bit.ly/spam123 Check this out tinyurl.com/xyz"),
        
        # Test 12: Fake reviews with padding
        ("Padding spam", "Good teacher. " + "Great! " * 50),
        
        # Test 13: Whitespace manipulation
        ("Whitespace padding", "Good\n\n\n\n\n\n\n\n\n\nteacher\n\n\n\n\n\n\n"),
        
        # Test 14: Review bombing simulation
        ("Generic negative", "Bad professor. Not good. Terrible. Very bad. Not recommended."),
        
        # Test 15: Emoji flooding
        ("Emoji flood", "🔥🔥🔥 worst 🔥🔥🔥 lecturer 🔥🔥🔥 ever 🔥🔥🔥 seen 🔥🔥🔥"),
        
        # Test 16: Excessive mentions
        ("Mention spam", "@student1 @student2 @student3 This prof is bad " + " ".join([f"@user{i}" for i in range(15)])),
    ]
    
    for test_name, text in spam_tests:
        result = ContentModerator.moderate(text)
        print_result(test_name, text, result)
    
    # === DEFAMATION/HARMFUL CONTENT ===
    print("\n\n### DEFAMATION & HARMFUL CONTENT ###\n")
    
    defamation_tests = [
        # Test 17: False accusations (clean language but harmful)
        ("False accusation", "This lecturer accepts bribes and gives grades for money. Totally corrupt and unethical person."),
        
        # Test 18: Personal attacks (clean language)
        ("Personal attack", "This ugly old hag is disgusting to look at and should retire immediately."),
        
        # Test 19: Discriminatory (coded language)
        ("Coded discrimination", "This lecturer should go back to where they came from. Not qualified for this position."),
        
        # Test 20: Threats (veiled)
        ("Veiled threat", "Someone should teach this lecturer a lesson. They won't last long here."),
        
        # Test 21: Sexual harassment implications
        ("Sexual implications", "This lecturer is always looking at female students inappropriately and makes suggestive comments."),
    ]
    
    for test_name, text in defamation_tests:
        result = ContentModerator.moderate(text)
        print_result(test_name, text, result)
    
    # === SYSTEM MANIPULATION ===
    print("\n\n### SYSTEM MANIPULATION ATTEMPTS ###\n")
    
    system_tests = [
        # Test 22: SQL Injection attempt
        ("SQL injection", "'; DROP TABLE review; -- Great lecturer and very helpful teacher"),
        
        # Test 23: XSS attempt
        ("XSS attack", "<script>alert('xss')</script> Good professor and knowledgeable teacher"),
        
        # Test 24: HTML injection
        ("HTML injection", "<img src=x onerror=alert(1)> Excellent lecturer and great teaching style"),
        
        # Test 25: Command injection
        ("Command injection", "; rm -rf / && echo 'Good teacher' && cat /etc/passwd"),
        
        # Test 26: Template injection
        ("Template injection", "{{ 7*7 }} Good professor {{config}} and helpful teacher"),
    ]
    
    for test_name, text in system_tests:
        result = ContentModerator.moderate(text)
        print_result(test_name, text, result)
    
    # === LENGTH/QUALITY MANIPULATION ===
    print("\n\n### LENGTH & QUALITY MANIPULATION ###\n")
    
    quality_tests = [
        # Test 27: Minimum viable bypass
        ("Barely passing", "Bad teacher yes"),
        
        # Test 28: Nonsense that passes length
        ("Nonsense", "blah blah blah this lecturer blah blah blah bad blah blah"),
        
        # Test 29: Copy-paste repetition
        ("Copy-paste", "This lecturer is not good. " * 10),
        
        # Test 30: All caps legitimate concern
        ("ALL CAPS YELLING", "THIS LECTURER IS COMPLETELY UNPROFESSIONAL AND NEVER SHOWS UP TO CLASS ON TIME"),
        
        # Test 31: Gibberish keyboard mash
        ("Keyboard mash", "asdfghjkl qwertyuiop zxcvbnm this lecturer is terrible mnbvcxz"),
        
        # Test 32: Single character repetition with spaces
        ("Spaced repetition", "b a d   t e a c h e r   v e r y   b a d"),
    ]
    
    for test_name, text in quality_tests:
        result = ContentModerator.moderate(text)
        print_result(test_name, text, result)
    
    # === CONTEXT MANIPULATION ===
    print("\n\n### CONTEXT MANIPULATION ###\n")
    
    context_tests = [
        # Test 33: Sarcasm (legitimate but negative)
        ("Sarcasm", "Oh yeah, GREAT lecturer. Really AMAZING. Best professor EVER. Totally RECOMMEND. [sarcasm]"),
        
        # Test 34: Quoting others
        ("Quoting bypass", "Another student said 'this lecturer is fucking terrible' and I completely agree with that assessment."),
        
        # Test 35: Conditional profanity
        ("Conditional", "If I could use profanity, I would say this lecturer is the worst. But I'll just say very bad."),
        
        # Test 36: Acronym profanity
        ("Acronyms", "This lecturer is a total POS and SOB. What a complete PITA to deal with. GTFO."),
    ]
    
    for test_name, text in context_tests:
        result = ContentModerator.moderate(text)
        print_result(test_name, text, result)
    
    # === SUMMARY ===
    print("\n\n" + "=" * 80)
    print("STRESS TEST COMPLETE")
    print("=" * 80)
    print("\nVULNERABILITIES IDENTIFIED:")
    print("1. Leetspeak (f4ck, sh1t, @ss, b!tch)")
    print("2. Symbol substitution (f*ck, sh*t, @ss)")
    print("3. Homoglyphs and Unicode tricks")
    print("4. Common misspellings (fuk, shyt, phuck)")
    print("5. Defamatory content with clean language")
    print("6. False accusations and personal attacks")
    print("7. Discriminatory coded language")
    print("8. System injection attempts (SQL, XSS, HTML)")
    print("9. Sarcasm and context manipulation")
    print("10. Acronyms (POS, SOB)")
    print("\nRECOMMENDATIONS:")
    print("- Add leetspeak normalization")
    print("- Add common misspelling detection")
    print("- Add symbol-to-letter mapping")
    print("- Add context analysis for defamation")
    print("- Add HTML/script sanitization")
    print("- Add sentiment analysis")
    print("- Add phrase-level detection beyond single words")
    print("=" * 80)

if __name__ == '__main__':
    run_stress_tests()
