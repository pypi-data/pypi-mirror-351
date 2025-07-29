def classify_unicode(input_text):
    """
    Classifies input text into categories:
    - Raw Tamil Unicode
    - Tamil + English Unicode
    - English Unicode
    - Numeric
    - Mixed (Tamil + English + Numeric)

    Args:
        input_text (str): The input text to classify.

    Returns:
        str: Classification type ('raw_tamil', 'mixed', 'english', 'numeric', 'mixed_all')
    """
    tamil_characters = range(0x0B80, 0x0BFF + 1)  # Tamil Unicode range
    input_text_unicode_array = [ord(char) for char in input_text]
    contains_tamil = any(
        char in tamil_characters for char in input_text_unicode_array)
    contains_english = any(char.isascii() and char.isalpha()
                           for char in input_text)
    contains_numeric = any(char.isdigit() for char in input_text)

    if contains_english and contains_numeric:
        return "en_numeric"
    elif contains_tamil and contains_english:
        return "en_tamil"
    elif contains_tamil:
        return "raw_tamil"
    elif contains_numeric:
        return "numeric"
    else:
        return "english"
    