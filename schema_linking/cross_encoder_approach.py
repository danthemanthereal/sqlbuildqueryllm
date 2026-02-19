from sentence_transformers import SentenceTransformer, util

from data_preprocessing.german_spider_preprocessor import get_english_table_name
from data_preprocessing.preprocessor import reprocess
from data_preprocessing.stat_bot_swiss_preprocessing import table_meta_df, query_question_test_df
from schema_linking.custom_e_sql.get_table_based_value_in_col import get_relevant_tables_of_question
from structural_linking.gnn_spider_german_or_knowledge_graph import get_all_tables, get_graph, get_foreign_keys_of_table

model = SentenceTransformer('all-MiniLM-L6-v2')



def get_similarity_tables_and_sentence(sentence_tokens: list[str]):

    tables = get_all_tables()
    #lemmatized_tables = [reprocess(table) for table in tables]
    #lemmatized_tokens = [reprocess(token) for token in sentence_tokens]
    token_embeddings = model.encode(sentence_tokens)
    # for tables of german spider
   # table_embeddings = model.encode(tables)
    # for table embdegging swiss tat bot
    descriptions = table_meta_df["discription"].tolist()

    # Jeden String durch reprocess schicken
    #processed_descriptions = [reprocess(desc) for desc in descriptions]
    table_embeddings = model.encode(tables)
    threshold = 0.9
    relevant_tables = []
    temp_german = []

    for i, token_emb in enumerate(token_embeddings):
        for j, table_emb in enumerate(table_embeddings):
            similarity = util.cos_sim(token_emb, table_emb).item()
            if similarity >= threshold:
                #matching_row = table_meta_df[table_meta_df["discription"] == descriptions[j]]
                #table_value = ""
                #if not matching_row.empty:
                 #   table_value = matching_row.iloc[0]["name"]  # Name der ersten passenden Zeile
                  #  print(f"Name der Zeile mit Description '{descriptions[j]}': {table_value}")
                #print("Frage:", question)
               # print(f"Wort: {sentence_tokens[i]}")
                #print(f"Table {tables[j]}")
                english_table_name = get_english_table_name(tables[i])

                #print(f" fks {possible_joined_tables}")
                get_english = get_english_table_name(tables[j])
               # temp_german.append(tables[j])
                relevant_tables.append(get_english)
               # print("Table ", table_value)
               # matchingquery = query_question_test_df[query_question_test_df["question"] == question]
               # query_value = ""
               # if not matchingquery.empty:
                    # Direkt den Wert der 'query'-Spalte holen
                #    query_value = matchingquery.iloc[0]["query"]
               # print("Query ", query_value)
               # print(f"is in query {table_value in query_value}")
                #print(f"Ähnlichkeit: {similarity:.3f}\n")
    # add with value based
    rel_tabes_based_col_values = get_relevant_tables_of_question(" ".join(sentence_tokens))
    if rel_tabes_based_col_values:
        for german_table in rel_tabes_based_col_values:
            relevant_tables.append(get_english_table_name(german_table))
    return relevant_tables