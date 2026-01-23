import nltk
import spacy
from nltk import SnowballStemmer
from nltk.stem.porter import *
nlp = spacy.load("de_core_news_sm")

def reprocess(text:str):
    lowred_text = _lower_text(text)
    tokens = _tokenize(text)
    non_stop_word_tokens = _get_non_stop_words(tokens)
    lemmatizes = _lemmatize(non_stop_word_tokens)
    pos_tags = _get_pos_tag(tokens) # anwenden auf non stop tokens ? 

def _lower_text(text: str) -> str:
    return text.lower()

def _tokenize(text: str):
    return nlp(text)

def _get_non_stop_words(tokens):
    return [token for token in tokens if not _is_full_word_or_punctuation(token)]

def _is_full_word_or_punctuation(token)->bool:
    return token.is_stop or token.is_punct or token.is_space # token.text.strip() ?

def _lemmatize(tokens):
    lemma = []
    for token in tokens:
        lemma.append(token.lemma_.lower())
    return " ".join(lemma)

def _get_pos_tag(tokens):
    """
    pos_tag_map = {}
    for token in tokens:
        pos_tag_map[token.text] = token.pos_
    :return pos_tag_map
    """
    return nltk.pos_tag(tokens, lang="deu")

def _get_all_sentences(doc):
    sentences = []
    for sent in doc.sents:
        sentences.append(sent.text)
    return sentences


"""
import string
import nltk

def remove_punctuation(text):
    return "".join(char for char in text if char not in string.punctuation)

def clean_text(text, stop_words):
    # Convert to lowercase
    text = text.lower()

    # Remove punctuation 
    text = remove_punctuation(text)
    
    # Remove punctuation  
    # text = re.sub(r'[\W_]+', ' ', text)

    # Tokenize text
    words = nltk.word_tokenize(text)

    # Remove stopwords
    filtered_words = [word for word in words if word not in stop_words]

    return " ".join(filtered_words)
"""
# stemmin -> braucht nltk stemming -> dann lemmatize immer  ?

def port_stemming(tokens: list):
    stemmer = PorterStemmer()
    return [stemmer.stem(token) for token in tokens]

def snowball_stemming(tokens: list):
    stemmer = SnowballStemmer("german")
    return [ stemmer.stem(token) for token in tokens]

def get_lower_input(input_text: str):
    return input_text.lower()