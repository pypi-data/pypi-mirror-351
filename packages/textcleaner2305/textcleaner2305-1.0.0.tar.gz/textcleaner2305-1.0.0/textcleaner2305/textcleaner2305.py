import re
import string

def clean(text):
    """
    Clean text and return an array of lowercase words.
    
    Args:
        text (str): Input text to clean
        
    Returns:
        list: List of cleaned lowercase words
        
    Example:
        >>> from textcleaner import clean
        >>> clean("Hello, WORLD!! This is an example.")
        ['hello', 'world', 'this', 'is', 'an', 'example']
    """
    if not isinstance(text, str):
        return []
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and special characters
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Split into words and remove empty strings
    words = [word.strip() for word in text.split() if word.strip()]
    
    # Filter out numbers if desired (optional)
    # words = [word for word in words if not word.isdigit()]
    
    return words