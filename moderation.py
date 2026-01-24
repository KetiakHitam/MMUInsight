"""
Auto-moderation system for review content
Detects spam, profanity, and low-quality content
"""

import re
from typing import Tuple, List

PROFANITY_WORDS = {
    'fuck', 'fucks', 'fucker', 'fuckers', 'fucking', 'fucked', 'fuckface', 'fuckhead', 
    'shit', 'shits', 'shitter', 'shitters', 'shitty', 'shithead', 'shitface', 'bullshit',
    'ass', 'asses', 'asshole', 'assholes', 'asshat', 'dumbass', 'badass', 'jackass',
    'bitch', 'bitches', 'bitchy', 'bitching', 'son of a bitch',
    'bastard', 'bastards',
    'dick', 'dicks', 'dickhead', 'dickface',
    'cock', 'cocks', 'cocksucker',
    'pussy', 'pussies',
    'cunt', 'cunts',
    'piss', 'pissed', 'pissing',
    'crap', 'crappy',
    'whore', 'whores',
    'slut', 'sluts', 'slutty',
    'retard', 'retards', 'retarded', 'retardation',
    'fag', 'fags', 'faggot', 'faggots',
    'nigga', 'niggas', 'nigger', 'niggers', 'nga',
    'chink', 'chinks',
    'spic', 'spics',
    'gook', 'gooks',
    'kike', 'kikes',
    'beaner', 'beaners',
    'wetback', 'wetbacks',
    'raghead', 'ragheads',
    'cracker', 'crackers',
    'honkey', 'honky',
    'tranny', 'trannies',
    'dyke', 'dykes',
    'homo', 'homos',
    'motherfucker', 'motherfuckers',
    'wanker', 'wankers',
    'twat', 'twats',
    'prick', 'pricks',
    'douche', 'douchebag', 'douchebags',
    'tits', 'titties',
    'boobs', 'boobies',
    'penis', 'penises',
    'vagina', 'vaginas',
    'anal',
    'anus',
    'dildo', 'dildos',
    'retard', 'retards', 'retarded',
    'moron', 'morons', 'moronic',
    'idiot', 'idiots', 'idiotic',
    'imbecile', 'imbeciles',
    'scumbag', 'scumbags',
    'loser', 'losers',
    'trash', 'trashy',
    'whore', 'whoring',
    'rape', 'raping', 'rapist', 'raped',
    'nazi', 'nazis',
    'terrorist', 'terrorists',
}

class ModerationResult:
    """Result of content moderation"""
    def __init__(self, is_clean: bool, flags: List[str], severity: str = 'low'):
        self.is_clean = is_clean  
        self.flags = flags 
        self.severity = severity  
        self.requires_review = not is_clean
    
    def __repr__(self):
        return f"ModerationResult(clean={self.is_clean}, flags={self.flags}, severity={self.severity})"


class ContentModerator:
    """Auto-moderation system for reviews and replies"""
    
    MIN_LENGTH = 10 
    MAX_LENGTH = 5000  
    MIN_WORDS = 3  
    MAX_CAPS_RATIO = 0.3  
    MAX_REPEATED_CHARS = 5  
    MAX_REPEATED_WORDS = 5 
    
    _VOWELS = frozenset('aeiou')
    _COMMON_WORDS = frozenset({
        'duck', 'ducks', 'luck', 'lucky', 'suck', 'truck', 'stuck', 'buck', 'muck', 'puck', 'tuck',
        'class', 'classes', 'glass', 'grass', 'pass', 'passing', 'mass', 'bass',
    })
    _PUNCTUATION_REGEX = re.compile(r'[^\w\s]')
    _REPEATED_CHARS_REGEX = re.compile(r'(.)\1{5,}')
    _MENTIONS_REGEX = re.compile(r'@\w+')
    _URL_REGEX = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    _CONSONANT_SEQ_REGEX = re.compile(r'[bcdfghjklmnpqrstvwxyz]{4,}')
    _SPACED_WORD_REGEX = re.compile(r'\b(\w)\s+(?=\w\s|\w$)')
    _LEET_CLEANUP_REGEX = re.compile(r'[_\-\*]')
    
    _LEET_TRANS = str.maketrans({
        '@': 'a', '4': 'a', '8': 'b', '(': 'c', '3': 'e',
        '6': 'g', '9': 'g', '#': 'h', '1': 'i', '!': 'i',
        '|': 'i', '0': 'o', '5': 's', '$': 's', '7': 't',
        '+': 't', '2': 'z', '_': '', '-': '', '*': ''
    })
    
    @staticmethod
    def normalize_leetspeak(text: str) -> str:
        """Convert leetspeak to normal text using optimized translation table"""
        return text.lower().translate(ContentModerator._LEET_TRANS)
    
    @staticmethod
    def add_vowel_variations(text: str) -> List[str]:
        """Generate variations by adding vowels to words that might have them removed"""
        words = text.split()
        variations = []
        vowels = ContentModerator._VOWELS
        
        for word in words:
            if len(word) < 3:
                continue
            
            word_lower = word.lower()
            
            if word_lower in ContentModerator._COMMON_WORDS:
                continue
            
            word_no_vowels = ''.join(c for c in word_lower if c not in vowels)
            
            if not word_no_vowels or len(word_no_vowels) < 2:
                continue
            
            for profanity in PROFANITY_WORDS:
                if len(profanity) < 3:
                    continue
                
                profanity_no_vowels = ''.join(c for c in profanity if c not in vowels)
                
                if word_no_vowels == profanity_no_vowels:
                    variations.append(profanity)
                    break
        
        return variations
    
    MISSPELLING_MAP = {
        'fuk': 'fuck', 'fuq': 'fuck', 'fook': 'fuck', 'phuck': 'fuck', 'fux': 'fuck', 'fucc': 'fuck', 'phuk': 'fuck', 'fock': 'fuck', 'fukk': 'fuck', 'fuhk': 'fuck',
        'fuking': 'fucking', 'fkn': 'fucking', 'fking': 'fucking',
        'shyt': 'shit', 'shite': 'shit', 'shiit': 'shit', 'sht': 'shit', 'shiet': 'shit', 'shiiet': 'shit', 'sheeit': 'shit', 'shizz': 'shit', 'shiz': 'shit', 'shiite': 'shit',
        'azz': 'ass', 'asz': 'ass', 'azzz': 'ass', 'azs': 'ass', 'ahole': 'asshole', 'asss': 'ass',
        'biotch': 'bitch', 'biatch': 'bitch', 'byatch': 'bitch', 'betch': 'bitch', 'beotch': 'bitch', 'bioch': 'bitch', 'beatch': 'bitch', 'beyotch': 'bitch', 'bizatch': 'bitch', 'biitch': 'bitch', 'beyatch': 'bitch',
        'cnt': 'cunt', 'kunt': 'cunt', 'cnut': 'cunt',
        'dik': 'dick', 'dck': 'dick', 'dikk': 'dick', 'dicc': 'dick',
        'fgt': 'fag', 'phag': 'fag',
        'nig': 'nigger', 'n1g': 'nigger', 'niga': 'nigger', 'nibba': 'nigger', 'nigg': 'nigger', 'niqqa': 'nigger', 'n1gger': 'nigger',
        'pis': 'piss', 'pizz': 'piss',
        'kok': 'cock', 'cok': 'cock', 'cocc': 'cock', 'cox': 'cock',
        'basterd': 'bastard', 'baztard': 'bastard', 'bustard': 'bastard',
        'whoar': 'whore', 'hore': 'whore', 'wh0re': 'whore', 'hoar': 'whore',
        'slu': 'slut', 'sloot': 'slut',
        'prik': 'prick', 'pric': 'prick',
        'twot': 'twat',
        'kunte': 'cunt',
        'douchbag': 'douchebag', 'douch': 'douche', 'doosh': 'douche',
        'motha': 'motherfucker', 'mutha': 'motherfucker', 'mofo': 'motherfucker', 'muthafucka': 'motherfucker', 'mothafucka': 'motherfucker',
    }
    
    @staticmethod
    def check_misspellings(clean_text: str) -> List[str]:
        """Detect common intentional misspellings using optimized lookup table"""
        misspelling_map = ContentModerator.MISSPELLING_MAP
        return [
            f"{mapped} (misspelled as '{word}')"
            for word in clean_text.split()
            if (mapped := misspelling_map.get(word)) and mapped in PROFANITY_WORDS
        ]
    
    @staticmethod
    def check_profanity(text: str) -> Tuple[bool, List[str]]:
        """Check for profanity in text with optimized processing"""
        text_lower = text.lower()
        normalized_text = ContentModerator.normalize_leetspeak(text_lower)
        
        punct_regex = ContentModerator._PUNCTUATION_REGEX
        clean_text = punct_regex.sub('', text_lower)
        clean_normalized = punct_regex.sub('', normalized_text)
        
        spaced_regex = ContentModerator._SPACED_WORD_REGEX
        spaced_text = spaced_regex.sub(r'\1', clean_text)
        spaced_normalized = spaced_regex.sub(r'\1', clean_normalized)
        
        found_profanity = set()
        
        for word in clean_text.split():
            if word in PROFANITY_WORDS:
                found_profanity.add(word)
        
        for word in clean_normalized.split():
            if word in PROFANITY_WORDS:
                found_profanity.add(f"{word} (leetspeak)")
        
        for word in spaced_text.split():
            if word in PROFANITY_WORDS:
                found_profanity.add(f"{word} (spaced)")
        
        for word in spaced_normalized.split():
            if word in PROFANITY_WORDS:
                found_profanity.add(f"{word} (spaced+leetspeak)")
        
        for word in ContentModerator.add_vowel_variations(clean_text):
            found_profanity.add(f"{word} (vowels removed)")
        
        for word in ContentModerator.add_vowel_variations(clean_normalized):
            found_profanity.add(f"{word} (vowels+leetspeak)")
        
        found_profanity.update(ContentModerator.check_misspellings(clean_text))
        
        if found_profanity:
            return False, [f"profanity_detected: {', '.join(found_profanity)}"]
        
        return True, []
    
    @staticmethod
    def check_spam_patterns(text: str) -> Tuple[bool, List[str]]:
        """Check for spam patterns using pre-compiled regex"""
        flags = []
        
        urls = ContentModerator._URL_REGEX.findall(text)
        if len(urls) > 2:
            flags.append(f"excessive_links: {len(urls)} found")
            return False, flags
        
        if ContentModerator._REPEATED_CHARS_REGEX.search(text):
            flags.append("excessive_character_repetition")
            return False, flags
        
        mentions = ContentModerator._MENTIONS_REGEX.findall(text)
        if len(mentions) > 10:
            flags.append(f"excessive_mentions: {len(mentions)}")
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
        """Check for gibberish/keyboard mash using optimized sampling"""
        sample = text[::5].lower()
        consonant_sequences = len(ContentModerator._CONSONANT_SEQ_REGEX.findall(sample))
        
        if consonant_sequences > 5:
            return False, ["possible_gibberish: excessive consonant sequences"]
        
        return True, []
    
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
