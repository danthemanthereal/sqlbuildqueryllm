import spacy
nlp = spacy.load("de_core_news_sm")

def reprocess(text:str):
    _tokenize(text)

def _tokenize(text:str):
    doc = nlp(text)

    tokens = []
    for token in doc:
        if token.is_stop:
            continue
        if token.is_punct:
            continue
        if token.is_space:
            continue

        tokens.append(token.lemma_.lower())

    return " ".join(tokens)


