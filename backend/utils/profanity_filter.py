"""
Simple profanity filter for usernames and content
"""

# List of inappropriate words to filter
# This is a basic list - you can expand it as needed
BAD_WORDS = {
    # Common profanity
    "fuck", "shit", "bitch", "ass", "damn", "crap", "piss", "dick",
    "cock", "pussy", "fag", "bastard", "slut", "whore", "nigger", "nigga",
    "cunt", "twat", "wank", "bollocks", "prick", "douche", "turd",
    
    # Variations and common bypasses
    "fck", "fuk", "sht", "btch", "dck", "cck", "cnt", "fag", "fgt",
    "fck", "azz", "asz", "shyt", "b1tch", "d1ck", "fvck", "sh1t",
    "a55", "b!tch", "d!ck", "sh!t", "f*ck", "b*tch", "c*nt",
    
    # Offensive terms
    "nazi", "hitler", "retard", "rape", "molest", "pedo", "pedophile",
    
    # Add more as needed...
}


def contains_profanity(text: str) -> bool:
    """
    Check if text contains any profanity
    
    Args:
        text: String to check (username, email, etc.)
    
    Returns:
        True if profanity is found, False otherwise
    """
    if not text:
        return False
    
    # Convert to lowercase for checking
    text_lower = text.lower()
    
    # Check for exact matches and substrings
    for bad_word in BAD_WORDS:
        if bad_word in text_lower:
            return True
    
    return False


def get_profanity_error_message() -> str:
    """Get a user-friendly error message for profanity detection"""
    return "Username or email contains inappropriate content. Please choose a different one."


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username for profanity
    
    Args:
        username: Username to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if contains_profanity(username):
        return False, get_profanity_error_message()
    
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email for profanity (checks local part before @)
    
    Args:
        email: Email to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return True, ""
    
    # Check the part before @ symbol
    local_part = email.split('@')[0] if '@' in email else email
    
    if contains_profanity(local_part):
        return False, get_profanity_error_message()
    
    return True, ""
