"""
Auto-moderation system for review content
Detects spam, profanity, and low-quality content
"""

import re
from typing import Tuple, List

# profanity word list (can be expanded)
PROFANITY_WORDS = {
    'fuck', 'shit', 'ass', 'bitch', 'retard', 'damn', 'crap', 'piss', 'bastard',
    'asshole', 'dick', 'cock', 'pussy', 'whore', 'slut', 'cunt', 'motherfucker',
    'fucker',
}

class ModerationResult:
    """Result of content moderation"""
    def __init__(self, is_clean: bool, flags: List[str], severity: str = 'low'):
        self.is_clean = is_clean  # True if content passes all checks
        self.flags = flags  # List of issues found
        self.severity = severity  # 'low', 'medium', 'high'
        self.requires_review = not is_clean
    
    def __repr__(self):
        return f"ModerationResult(clean={self.is_clean}, flags={self.flags}, severity={self.severity})"


class ContentModerator:
    """Auto-moderation system for reviews and replies"""
    
    MIN_LENGTH = 10  # Minimum character length
    MAX_LENGTH = 5000  # Maximum character length
    MIN_WORDS = 3  # Minimum word count
    MAX_CAPS_RATIO = 0.3  # Max allowed ratio of capital letters
    MAX_REPEATED_CHARS = 5  # Max repeated characters in a row
    MAX_REPEATED_WORDS = 5  # Max allowed repetitions of same word
    
    @staticmethod
    def check_profanity(text: str) -> Tuple[bool, List[str]]:
        """Check for profanity in text"""
        flags = []
        text_lower = text.lower()
        
        clean_text = re.sub(r'[^\w\s]', '', text_lower)
        words = clean_text.split()
        
        found_profanity = []
        for word in words:
            if word in PROFANITY_WORDS:
                found_profanity.append(word)
        
        if found_profanity:
            flags.append(f"profanity_detected: {', '.join(set(found_profanity))}")
            return False, flags
        
        return True, flags
    
    @staticmethod
    def check_spam_patterns(text: str) -> Tuple[bool, List[str]]:
        """Check for spam patterns"""
        flags = []
        
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if len(urls) > 2:
            flags.append(f"excessive_links: {len(urls)} found")
            return False, flags
        
        if re.search(r'(.)\1{' + str(ContentModerator.MAX_REPEATED_CHARS) + ',}', text):
            flags.append("excessive_character_repetition")
            return False, flags
        
        mentions = len(re.findall(r'@\w+', text))
        if mentions > 10:
            flags.append(f"excessive_mentions: {mentions}")
            return False, flags
        
        return True, flags
    
    @staticmethod
    def check_length(text: str) -> Tuple[bool, List[str]]:
        """Check text length validity"""
        flags = []
        
        if len(text) < ContentModerator.MIN_LENGTH:
            flags.append(f"too_short: {len(text)} chars (min: {ContentModerator.MIN_LENGTH})")
            return False, flags
        
        if len(text) > ContentModerator.MAX_LENGTH:
            flags.append(f"too_long: {len(text)} chars (max: {ContentModerator.MAX_LENGTH})")
            return False, flags
        
        words = text.split()
        if len(words) < ContentModerator.MIN_WORDS:
            flags.append(f"insufficient_content: {len(words)} words (min: {ContentModerator.MIN_WORDS})")
            return False, flags
        
        return True, flags
    
    @staticmethod
    def check_caps_lock_abuse(text: str) -> Tuple[bool, List[str]]:
        """Check for excessive capital letters"""
        flags = []
        
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return True, flags
        
        uppercase_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        
        if uppercase_ratio > ContentModerator.MAX_CAPS_RATIO:
            flags.append(f"caps_lock_abuse: {uppercase_ratio*100:.1f}% uppercase")
            return False, flags
        
        return True, flags
    
    @staticmethod
    def check_repeated_words(text: str) -> Tuple[bool, List[str]]:
        """Check for excessive word repetition"""
        flags = []
        
        words = text.lower().split()
        word_counts = {}
        
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        repeated = [(word, count) for word, count in word_counts.items() 
                   if count > ContentModerator.MAX_REPEATED_WORDS and len(word) > 2]
        
        if repeated:
            for word, count in repeated[:3]: 
                flags.append(f"word_repetition: '{word}' repeated {count} times")
            return False, flags
        
        return True, flags
    
    @staticmethod
    def check_gibberish(text: str) -> Tuple[bool, List[str]]:
        """Check for gibberish/keyboard mash"""
        flags = []
        
        vowels = 'aeiouAEIOU'
        consonants = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
        
        sample = text[::5]
        
        consonant_sequences = len(re.findall(r'[bcdfghjklmnpqrstvwxyz]{4,}', sample.lower()))
        
        if consonant_sequences > 5:
            flags.append("possible_gibberish: excessive consonant sequences")
            return False, flags
        
        return True, flags
    
    @classmethod
    def moderate(cls, text: str, content_type: str = 'review') -> ModerationResult:
        """
        Perform full moderation on content
        
        Args:
            text: Content to moderate
            content_type: Type of content ('review', 'reply', 'bio')
        
        Returns:
            ModerationResult object with flags and severity
        """
        
        all_flags = []
        severity = 'low'
        
        checks = [
            cls.check_length,
            cls.check_profanity,
            cls.check_spam_patterns,
            cls.check_caps_lock_abuse,
            cls.check_repeated_words,
            cls.check_gibberish,
        ]
        
        for check in checks:
            is_clean, flags = check(text)
            all_flags.extend(flags)
            
            if not is_clean:
                if 'profanity' in str(flags):
                    severity = 'high'
                elif any(x in str(flags) for x in ['too_short', 'insufficient_content']):
                    severity = 'low'
                elif 'gibberish' in str(flags):
                    severity = 'medium'
                else:
                    severity = 'medium'
        
        is_clean = len(all_flags) == 0
        
        return ModerationResult(
            is_clean=is_clean,
            flags=all_flags,
            severity=severity
        )


def get_moderation_summary(flags: List[str]) -> str:
    """Generate human-readable summary of moderation flags"""
    if not flags:
        return "Content passed all checks."
    
    summary_parts = []
    for flag in flags:
        if 'profanity' in flag:
            summary_parts.append("Contains profanity")
        elif 'too_short' in flag:
            summary_parts.append("Content too short")
        elif 'too_long' in flag:
            summary_parts.append("Content too long")
        elif 'caps_lock' in flag:
            summary_parts.append("Excessive capitalization")
        elif 'spam' in flag or 'links' in flag:
            summary_parts.append("Potential spam content")
        elif 'gibberish' in flag:
            summary_parts.append("Possible spam/gibberish")
        elif 'repetition' in flag:
            summary_parts.append("Excessive word repetition")
    
    return "; ".join(summary_parts)
