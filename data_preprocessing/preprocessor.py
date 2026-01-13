import spacy
nlp = spacy.load("de_core_news_sm")

def reprocess(text:str):
    _tokenize(text)

def _lemmatize(text:str):
    lemma = []
    tokens = _tokenize(text)
    for token in tokens:
        if _is_full_word_or_punctuation(token):
            continue
        lemma.append(token.lemma_.lower())
    return " ".join(lemma)

def _tokenize(text:str):
     return nlp(text)

def _is_full_word_or_punctuation(token)->bool:
    return token.is_stop or token.is_punct or token.is_space

def _get_all_sentences(doc):
    sentences = []
    for sent in doc.sents:
        sentences.append(sent.text)
    return sentences

# stemmin ?