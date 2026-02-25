from schema_linking.custom_chess_agentframe_work.information_retriever_agent.extract_key_words import get_key_words_nlp
from schema_linking.custom_chess_agentframe_work.information_retriever_agent.retrieve_entities import \
    find_columns_by_semantic


def get_relevant_tables(question: str):
    key_words = get_key_words_nlp(question)
    #similar_columns = find_columns_by_semantic(question, key_words, "")
    #print(similar_columns)

