from schema_linking.custom_chess_agentframe_work.faiss_db_in_chess import get_top_5_tables_based_on_key_word_meaning
from schema_linking.custom_chess_agentframe_work.information_retriever_agent.extract_key_words import get_key_words_nlp
from schema_linking.custom_chess_agentframe_work.information_retriever_agent.retrieve_context import \
    find_predicted_tables
from schema_linking.custom_chess_agentframe_work.information_retriever_agent.retrieve_entities import \
    find_columns_by_semantic


def get_relevant_tables(question: str):
    key_words = get_key_words_nlp(question)
    predicted_tables = []
    similar_columns = find_columns_by_semantic(question, key_words, "")
    for similar_column in similar_columns:
        first_part = similar_column[0]
        word = first_part.split(": `")[1]
        predicted_tables.append(word)

    res = find_predicted_tables(question, question, key_words,5)
    table_names = []
    for entry in res:
        # Zeilen splitten und nach "Tabelle: " suchen
        for line in entry.splitlines():
            line = line.strip()
            if line.startswith("Tabelle: "):
                table_name = line.replace("Tabelle: ", "").strip()
                table_names.append(table_name)
                predicted_tables.append(table_name)
    #table_embedding = get_top_5_tables_based_on_key_word_meaning(key_words)
    #predicted_tables.extend(table_embedding)
    return predicted_tables

