# Schritt 1 : sucht Keywords (Tabellen, Spalten, ... ) aus Frage
from data_preprocessing.preprocessor import reprocess


def return_extracted_key_words(question: str) -> list:

    """
    Funktioiert so man gibt Frage und Promot
    bekommt Liste von Key wortts potenzielle Tablellen , Spalten, Bedingungen ? ....
    :param question:
    :return:
    """
    keywords = []
    return keywords

# eigentlich llm  hier testweise einfach mit spacy so stop wörter usw entfernen

def get_key_words_nlp(question: str) -> list:
    return reprocess(question)