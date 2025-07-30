import re
from promptcompression import compress, replace_contractions, tokens

def test_replace_contractions():
    text = "I can not go because I do not want to."
    expected = "I can't go because I don't want to."
    result = replace_contractions(text)
    assert result == expected

def test_tokens_calculation():
    original = "This is an example sentence."
    cleaned = "exampl sentenc"
    saved, ratio = tokens(original, cleaned)
    assert isinstance(saved, int)
    assert isinstance(ratio, float)
    assert saved > 0
    assert 0 <= ratio <= 1

def test_compress_basic():
    input_text = "This is a TEST with multiple!!! punctuation marks?? and stopwords."
    compressed = compress(input_text)
    assert isinstance(compressed, str)
    assert "!!!" not in compressed
    assert len(compressed.split()) < len(input_text.split())

def test_compress_with_savings():
    input_text = "He did not know what was not right."
    result = compress(input_text, savings=True)
    assert isinstance(result, tuple)
    compressed_text, tokens_saved, ratio = result
    assert isinstance(compressed_text, str)
    assert isinstance(tokens_saved, int)
    assert isinstance(ratio, float)
    assert 0 <= ratio <= 1

def test_compress_empty_string():
    result = compress("", savings=True)
    assert result == ("", 0, 0)

def test_idempotency():
    text = "I will not go there because I do not like it!"
    once = compress(text)
    twice = compress(once)
    assert once == twice