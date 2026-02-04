"""
ASCII Art Detection System
Detects suspicious ASCII art patterns to flag reviews for moderation
"""
import re


class AsciiArtDetector:
    """
    Detects ASCII art in user-generated content using multi-factor scoring.
    Flags content that scores >= 2 factors AND is > 100 chars.
    """
    
    # Characters commonly used in ASCII art (excluding normal punctuation)
    ASCII_SYMBOLS = set('~^|\\/*+=[]{}<>@#$%&')
    NORMAL_PUNCT = set('.,!?\'"-()')
    
    @staticmethod
    def detect_ascii_art(text):
        """
        Analyze text for ASCII art patterns using multi-factor scoring.
        
        Args:
            text (str): User input to analyze
            
        Returns:
            dict: {
                'is_flagged': bool,
                'score': int (0-4),
                'factors': list of triggered factors,
                'severity': 'low'|'medium'|'high'|None
            }
        """
        if not text or len(text.strip()) < 100:
            # Skip detection for short content
            return {
                'is_flagged': False,
                'score': 0,
                'factors': [],
                'severity': None
            }
        
        lines = text.split('\n')
        score = 0
        factors = []
        
        # Factor 1: Line Structure (whitespace + symbols pattern)
        if AsciiArtDetector._check_line_structure(lines):
            score += 1
            factors.append('line_structure')
        
        # Factor 2: Dense Symbol Lines
        if AsciiArtDetector._check_dense_symbols(lines):
            score += 1
            factors.append('dense_symbols')
        
        # Factor 3: Repetition Patterns
        if AsciiArtDetector._check_repetition(text):
            score += 1
            factors.append('repetition')
        
        # Factor 4: Indentation Pattern (code block-like)
        if AsciiArtDetector._check_indentation(lines):
            score += 1
            factors.append('indentation')
        
        is_flagged = score >= 2
        severity = None
        if is_flagged:
            severity = 'high' if score >= 3 else 'medium'
        
        return {
            'is_flagged': is_flagged,
            'score': score,
            'factors': factors,
            'severity': severity
        }
    
    @staticmethod
    def _check_line_structure(lines):
        """
        Check if lines have leading/trailing spaces + symbols (ASCII art formatting).
        Returns True if >30% of non-empty lines match this pattern.
        """
        if not lines:
            return False
        
        matched = 0
        for line in lines:
            if not line.strip():
                continue
            
            # Check for leading/trailing spaces AND contains ASCII symbols
            has_leading_space = line != line.lstrip()
            has_trailing_space = line != line.rstrip()
            has_ascii_symbols = any(c in AsciiArtDetector.ASCII_SYMBOLS for c in line)
            
            if (has_leading_space or has_trailing_space) and has_ascii_symbols:
                matched += 1
        
        total_non_empty = sum(1 for line in lines if line.strip())
        if total_non_empty == 0:
            return False
        
        return matched / total_non_empty > 0.3
    
    @staticmethod
    def _check_dense_symbols(lines):
        """
        Check if any line has >50% dangerous ASCII art symbols.
        Excludes normal punctuation.
        """
        for line in lines:
            if not line.strip():
                continue
            
            # Count dangerous symbols vs alphanumeric
            dangerous = sum(1 for c in line if c in AsciiArtDetector.ASCII_SYMBOLS)
            total = len(line)
            
            if total > 0 and dangerous / total > 0.5:
                return True
        
        return False
    
    @staticmethod
    def _check_repetition(text):
        """
        Check for 4+ consecutive identical non-letter characters.
        Exclude common punctuation: . - '
        """
        # Pattern: 4+ identical characters that aren't letters, digits, or excluded chars
        pattern = r'([^\w.\-\'\s])\1{3,}'
        return bool(re.search(pattern, text))
    
    @staticmethod
    def _check_indentation(lines):
        """
        Check for multiple lines with consistent indentation (code block pattern).
        Returns True if >40% of lines have leading spaces (excluding first line).
        """
        if len(lines) < 3:
            return False
        
        indented = 0
        for line in lines[1:]:  # Skip first line
            if line and line[0] == ' ':
                indented += 1
        
        non_first = len(lines) - 1
        return non_first > 0 and indented / non_first > 0.4
