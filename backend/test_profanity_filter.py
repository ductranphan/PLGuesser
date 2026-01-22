"""
Test script for profanity filter
"""
from utils.profanity_filter import validate_username, validate_email, contains_profanity

def test_profanity_filter():
    print("\n" + "="*70)
    print("TESTING PROFANITY FILTER")
    print("="*70 + "\n")
    
    # Test usernames
    test_usernames = [
        ("john123", True, "Clean username"),
        ("player456", True, "Clean username"),
        ("fuck123", False, "Contains profanity"),
        ("shit_user", False, "Contains profanity"),
        ("asshole", False, "Contains profanity"),
        ("badword_bitch", False, "Contains profanity"),
        ("SomeB1tch", False, "Contains l33t speak profanity"),
        ("fckoff", False, "Contains shortened profanity"),
        ("awesome_player", True, "Clean username"),
    ]
    
    print("Testing Usernames:")
    print("-" * 70)
    for username, should_pass, description in test_usernames:
        is_valid, error = validate_username(username)
        status = "✅ PASS" if is_valid == should_pass else "❌ FAIL"
        print(f"{status} | '{username}' | {description}")
        if not is_valid:
            print(f"     Error: {error}")
    
    print("\n" + "="*70 + "\n")
    
    # Test emails
    test_emails = [
        ("john@example.com", True, "Clean email"),
        ("player123@gmail.com", True, "Clean email"),
        ("fuck123@example.com", False, "Profanity in local part"),
        ("badword@gmail.com", True, "Bad word is allowed domain"),
        ("shituser@test.com", False, "Profanity in local part"),
    ]
    
    print("Testing Emails:")
    print("-" * 70)
    for email, should_pass, description in test_emails:
        is_valid, error = validate_email(email)
        status = "✅ PASS" if is_valid == should_pass else "❌ FAIL"
        print(f"{status} | '{email}' | {description}")
        if not is_valid:
            print(f"     Error: {error}")
    
    print("\n" + "="*70)
    print("Testing complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_profanity_filter()
