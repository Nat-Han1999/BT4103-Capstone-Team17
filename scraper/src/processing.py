import json
import re

def remove_duplicates(text_list):
    """
    Remove duplicates from the text list while maintaining its order.

    Args:
        text_list: list of phrases.

    Returns:
        A list of words that are unique.
    """
    return list(dict.fromkeys(text_list))

def process_texts(text_list): 
    """
    Cleans text data.
    Words are converted to lower case. 
    Special characters removed
    '\n' characters replaced with space.
    
    Args:
        text_list: list of phrases.

    Returns:
        String: A cleaned list of phrases which are joined together as a string.
    """
    processed = []

    for word in text_list:
        word = word.lower() # convert text to lowercase 

        # replace & with 'and'
        word = re.sub(r'&', 'and', word)  

        # remove special characters from text (this also removes Sinhala language)
        # keep '+', '.', '?', '!' and '@' to improve contextual understanding
        word = re.sub(r'[^A-Za-z0-9\s@+.?!]', '', word)

        # replace \n with space
        word = re.sub(r'\n+', ' ', word) 

        if word not in processed and word != '': 
            processed.append(word)

    return " ".join(processed) # join list of texts into a single string

def process_extracted_texts(text_dictionary): 
    """
    Cleans extracted text data.
    Join all extracted texts into one string.
    
    Args:
        text_dictionary: Dictionary of extracted texts, key: links and values: extracted texts. 
    Returns:
        String: A cleaned list of extracted pdf/image texts joined together as a string.
    """
    result = ""
    
    for url, text in text_dictionary.items():
        if text is not None:
            text = text.lower()
            text = re.sub(r'&', 'and', text)  # replace & with 'and'
            text = re.sub(r'[^A-Za-z0-9\s@+?]', '', text) # keep '+', '?' and '@' 
            text = re.sub(r'\n+', ' ', text) # replace \n with space

            if text != ' ' and  text != '.':
                result += text

    return result