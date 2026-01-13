import spacy
import nltk
from nltk.stem.porter import *
nlp = spacy.load("de_core_news_sm")

def reprocess(text:str):
    tokens = _tokenize(text)
    lemmatizes = _lemmatize(tokens)


def _tokenize(text: str):
    return nlp(text)

def _lemmatize(tokens):
    lemma = []
    for token in tokens:
        if _is_full_word_or_punctuation(token):
            continue
        lemma.append(token.lemma_.lower())
    return " ".join(lemma)


def _is_full_word_or_punctuation(token)->bool:
    return token.is_stop or token.is_punct or token.is_space # token.text.strip() ?

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
# stemmin -> braucht nltk  ?

def stemming(tokens: list):
    stemmer = PorterStemmer()
    return [stemmer.stem(token) for token in tokens]