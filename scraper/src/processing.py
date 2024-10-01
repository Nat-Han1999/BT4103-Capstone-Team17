import json
import re

import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

def remove_duplicates(text_list):
    """Remove duplicates and words in remove list from the text list.

    Args:
        text_list: list of phrases.

    Returns:
        A list of words that are unique and not in the remove list.
    """
    removed = []
    for phrase in text_list: 
        words = phrase.split()
        for word in words: 
            if word:
                removed.append(word)
    return removed

def process_texts(text_list): 
    """Cleans text data but does not include stemming and lemmatization, simply cleans the text data.
      Trailing spaces are removed, words are converted to lower case. 
      Special characters and punctuations are removed from words.
      Removal of stop words.
    
    Args:
        text_list: list of phrases.

    Returns:
        A cleaned list of words.
    """
    processed = []
    stop_words = set(stopwords.words('english'))

    for word in text_list:
        word = word.strip().lower() # remove spaces and convert to lowercase 
        word = re.sub(r'[^A-Za-z0-9\s]', '', word) # remove special characters and punctuations from text (this also removes Sinhala language)
        word = re.sub(r'\n+', ' ', word) # replace \n with space
        if word and word not in stop_words: # remove stop words and empty strings
            processed.append(word) 

    return processed