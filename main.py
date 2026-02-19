from schema_linking.custom_e_sql.get_table_based_value_in_col import get_table_column_map, go_all_dbs, \
    get_table_column_map_per_db_id, construct_tokenized_db_table_value_corpus

from rank_bm25 import BM25Okapi


tokenized_db_corpus, db_corpuse = construct_tokenized_db_table_value_corpus()

bm25 = BM25Okapi(tokenized_db_corpus)

query = "Autodaten von 1970"

tokenized_query = query.split(" ")

scores = bm25.get_scores(tokenized_query)


import numpy as np

top_k = 5
top_indices = np.argsort(scores)[::-1][:top_k]


for idx in top_indices:
    table, column, value = db_corpuse[idx]
    print("Score:", scores[idx])
    print("Tabelle:", table)
    print("Spalte:", column)
    print("Wert:", value)
    print("-----")
