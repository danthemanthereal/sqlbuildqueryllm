import spacy
nlp = spacy.load("de_core_news_sm")

def reprocess(text:str):
    _tokenize(text)

def _tokenize(text:str):
    doc = nlp(text)

    tokens = []
    for token in doc:
        if _is_full_word_or_punctuation(token):
            continue
        tokens.append(token.lemma_.lower())

    return " ".join(tokens)

def _is_full_word_or_punctuation(token)->bool:
    return token.is_stop or token.is_punct or token.is_space

