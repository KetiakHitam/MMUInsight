"""
Sanitization utilities to prevent XSS attacks
"""
import bleach

def sanitize_user_content(text):
    """
    Sanitize user-generated content (reviews, replies, bios, etc.)
    Strips all HTML/JS except safe formatting tags
    
    Args:
        text (str): Raw user input
        
    Returns:
        str: Sanitized text safe to display
    """
    if not text:
        return text
    
    # Allow only these safe HTML tags
    allowed_tags = ['b', 'i', 'em', 'strong', 'a', 'p', 'br']
    
    # Allow only href for links (no onclick, onerror, etc.)
    allowed_attributes = {
        'a': ['href', 'title'],
    }
    
    # Strip any HTML/JS that's not in the allowed list
    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True  # Remove disallowed tags entirely
    )
