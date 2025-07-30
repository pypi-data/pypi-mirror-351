# Libraries
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import tiktoken
from typing import Union

# Dictionary of common contractions
contractions_dict = {
    "can not": "can't",
    "do not": "don't",
    "will not": "won't",
    "did not": "didn't",
    "has not": "hasn't",
    "have not": "haven't",
    "is not": "isn't",
    "are not": "aren't",
    "was not": "wasn't",
    "were not": "weren't",
    "would not": "wouldn't",
    "could not": "couldn't",
}

def replace_contractions(text: str) -> str:
    """
    Replaces the non-contracted words with their contraction

    Arg:
        text (str): The input text to process.

    Returns:
        str: The text with contractions.
    """

    for phrase, contraction in contractions_dict.items():
        pattern = re.compile(re.escape(phrase))
        text = pattern.sub(contraction, text)
    return text

def tokens(original_text: str, cleaned_text: str) -> tuple[int, float]:
    """
    Calculate token savings and compression ratio between original and cleaned text.

    Args:
        original_text (str): The original input text.
        cleaned_text (str): The cleaned version of the text.

    Returns:
        Tuple[int, float]: 
            - Tokens saved (int)
            - Compression ratio (float)
    """
    enc = tiktoken.get_encoding("cl100k_base")
    original_tokens = len(enc.encode(original_text))
    cleaned_tokens = len(enc.encode(cleaned_text))

    tokens_saved = original_tokens - cleaned_tokens
    compression_ratio = (tokens_saved / original_tokens) if original_tokens else 0

    return tokens_saved, compression_ratio

def compress(original_text: str, savings: bool = False) -> Union[str, tuple[str, int, float]]:
    """
    Compresses the input text by:
        - Lowercasing the text
        - Replacing phrases with contractions
        - Removing non-numeric special characters
        - Normalizing whitespace

    Args:
        original_text (str): The input text to process.
        savings (bool): If True, returns the number of tokens saved and the compression ratio.
    
    Returns:
        str: The processed text.
        int: Number of tokens saved (if savings is True).
        float: Compression ratio (if savings is True).
    """
    # Lowercasing the input text
    text = original_text.lower()

    # Replacing phrases with contractions
    text = replace_contractions(text)
    
    # Removing non-numeric special characters
    text = re.sub(r"[^a-z0-9\s]", "", text)
    
    # Normalizing whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Tokenizing
    text = text.split()
    
    # Removing stop words and stemming
    nltk.download('stopwords', quiet=True)
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    processed_words = []
    for w in text:
        if w not in stop_words:
            processed_words.append(stemmer.stem(w))

    cleaned_text = ' '.join(processed_words)
   
    if savings:
        tokens_saved, compression_ratio = tokens(original_text, cleaned_text)
        return cleaned_text, tokens_saved, compression_ratio
    
    return cleaned_text

# Example usage
test_example = 0 # Change to 1 to run the example
if test_example:
    sample_text = "Summarize this text while sounding more natural. Please do not use contractions or an em dash to be more human-like."
    result, tokens, ratio = compress(sample_text, savings=True)

    print("Compressed text:", result)
    print("Tokens saved:", tokens)
    print(f"Compression ratio: {ratio:.2f}")