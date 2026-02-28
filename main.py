import json
import os

from data_preprocessing.german_spider_preprocessor import get_english_table_name
from schema_linking.custom_auto_link.retrieval_of_faiss_db import get_top_k_columns
from schema_linking.custom_auto_link.vector_db_faiss import embed_documents
from schema_linking.custom_chess_agentframe_work.pipeline import get_relevant_tables
from schema_linking.use_table_name_as_anchor import get_most_similar_table_with_anchor

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import csv
import os
from difflib import SequenceMatcher
from time import sleep

from data_preprocessing.preprocessor import reprocess
from data_preprocessing.stat_bot_swiss_preprocessing import table_meta_df, only_german_test_df, query_question_test_df
from evaluation.eval_spider import execute_matching_check, check_precision, check_recall
from llm_components.groq.groq_llm_componnet import get_tables_groq
from llm_components.slim_sql_llm import get_sql_query
from schema_linking.c3_approach.tabell_recall_with_c3 import get_all_table_with_cols
from schema_linking.cross_encoder_approach import get_similarity_tables_and_sentence
from schema_linking.custom_e_sql.get_table_based_value_in_col import get_relevant_c3_tables
from schema_linking.custom_resd_sql.cross_encoder import get_relevant_tables_and_columns
from structural_linking.gnn_spider_german_or_knowledge_graph import get_gold_tables_of_db, get_db_id_and_tables, \
    get_all_tables_en, get_relations_per_db
from vector_database.vector_db_for_table_describtion_swit_bot_dataset import collection, embeddings, model
from transformers import AutoTokenizer
from torch import nn, cosine_similarity
from collections import Counter

"""only_table_name = list(table_meta_df["name"])
table_description_df = table_meta_df[["name", "discription"]]
only_question = list(only_german_test_df["question"])
query_end_question = query_question_test_df
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-german-cased")
embedding_dim = 768
table_embeddings = embeddings
table_in_query = 0
table_not_in_query = 0


for question in only_question:
    #pre_processed_words = reprocess(question)
    results = collection.query(
        query_texts=["".join([w.text for w in pre_processed_words]) + " datenbank tabelle beschreibung"],
        n_results=1
    )
    top_docs = results["documents"][0]
    top_scores = results["distances"][0]

    print("Query:", pre_processed_words)
    for doc, score in zip(top_docs, top_scores):
        print(score, doc)
    #tokens = tokenizer.tokenize(question)
    token_counts = Counter(tokens)
    input_ids = tokenizer(question, return_tensors="pt")["input_ids"]
    vocab = {token: idx for idx, token in enumerate(token_counts)}
    vocab_size = tokenizer.vocab_size
    word_embeddings = nn.Embedding(vocab_size, embedding_dim)(input_ids)
    bi_lstm = nn.LSTM(input_size=embedding_dim, hidden_size=128, bidirectional=True, batch_first=True)
    outputs, (hn, cn) = bi_lstm(word_embeddings)
    query_vector = outputs.mean(dim=1)
    #query_vector = model.encode(tokens, convert_to_tensor=True)
    #scores = cosine_similarity(query_vector, table_embeddings)
    #print("scores ")
    #print(scores)
    results = collection.query(
        query_texts=[question],
        n_results=8
    )

    query_wert = query_question_test_df.loc[query_question_test_df['question'] == question, 'query'].values[0]
    metadata_liste = results["metadatas"][0]

    ergebnis = any(item["name"] in query_wert for item in metadata_liste)
    if ergebnis is True:
        table_in_query += 1
    else:
        table_not_in_query += 1

print("table correct in query:", table_in_query)
print("table not in query:", table_not_in_query)


    #description = table_description_df.loc[table_description_df["name"] == table_name, "discription"].values[0]
    #print("richtiges ergebnis ",description )"""

csv_file = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/output.csv"
file_exists = os.path.isfile(csv_file)
header = ["question", "query", "some_tables_in_query","only_relevant_tables", "no_relevant_tables", "founded_tables", "method"]
with open(csv_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(header)



method = "cross-encoder"


def filter_aehnliche_woerter(zielwort, wortliste, threshold=0.8, ignore_case=True):
    """
    Gibt nur die Wörter zurück, deren Ähnlichkeit >= threshold ist.

    :param zielwort: Referenzwort
    :param wortliste: Liste von Wörtern
    :param threshold: Mindestähnlichkeit (0–1)
    :param ignore_case: Groß-/Kleinschreibung ignorieren
    :return: Gefilterte Liste
    """
    if ignore_case:
        zielwort = zielwort.lower()

    def aehnlichkeit(wort):
        if ignore_case:
            wort = wort.lower()
        return SequenceMatcher(None, zielwort, wort).ratio()

    return [wort for wort in wortliste if aehnlichkeit(wort) >= threshold]


def _get_relevant_tables(question_as_list: list[str]) -> list:
    return get_similarity_tables_and_sentence(question_as_list)

TOTAL = 1034
def get_percentage(amount: int):
    return round(amount / TOTAL * 100, 2)

def get_table_index(schema_entry):
    table_index = []
    for table_index_list in schema_entry["sql"]["from"].get("table_units", []):
        table_index.append(table_index_list[1])
    return table_index


json_file = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/dev_de.json"
hit_counter = 0
miss_counter = 0
no_table_counter = 0
precision_amount = 0
recall_amount = 0


#embed_documents(16)
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

for i, entry in enumerate(data):
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        question = "".join(entry.get("question"))
        print("Frage ", question)
        if entry.get('question'):
            found_some_table = False
            found_only_relevant_tables = False
            found_no_tables = False
            """groq_answer = get_tables_groq(entry.get('question'),i)
            sleep(60)
            print("groq answer: ", groq_answer)
            print(f"question {entry.get('question')}")"""
             #get_relevant_tables_and_columns(entry.get("question"))
           # relevant_tables, matched_value = get_relevant_c3_tables(" ".join(entry.get('question_toks')))
            """_get_relevant_tables(entry.get("question").split(" "))
            relevant_tables = [table for table in relevant_tables if table != ' ']
            tmp_similar_tables = []
            all_tables_en = get_all_tables_en()
            for table in relevant_tables:
                tmp_similar_tables.extend(filter_aehnliche_woerter(table, all_tables_en))
            relevant_tables.extend(tmp_similar_tables)
            possible_joined_tables = []
            for table in relevant_tables:
                possible_joined_tables.extend(get_relations_per_db(table))
            relevant_tables.extend(possible_joined_tables)"""
            relevant_tables = get_top_k_columns(entry.get("question"),5)
            relevant_tables = [r.get("metadata").get("table") for r in relevant_tables]
            #relevant_tables = [r.get("metadata").get("table") for r in relevant_tables]
            #relevant_tables = [dict.get("metadata", {}).get("table", " ") for dict in r]
            relevant_tables = list(dict.fromkeys(relevant_tables))
            print("predicted_tables in deutsch: ", relevant_tables)
            #relevant_tables = [get_english_table_name(table) for table in relevant_tables]
            flattened_tables = []

            for table in relevant_tables:
                flattened_tables.extend(get_english_table_name(table))

            relevant_tables = flattened_tables
            # similar schreibweise noch hinzu
            #similar_words = []
            #englisch_tables_name = get_all_tables_en()
            #for table in relevant_tables:
             #   sim_words = filter_aehnliche_woerter(table, englisch_tables_name, 0.8)
              #  similar_words.extend(sim_words)

            #relevant_tables.extend(similar_words)

            relevant_tables = list(dict.fromkeys(relevant_tables))
            print(f"predicted tables : {relevant_tables}")
           # print(f"matched values : {matched_value}")
            query = entry.get("query")
            query_lower = query.lower()
            if not relevant_tables:
                no_table_counter += 1
                found_no_tables = True
                continue

            if any(table.lower() in query_lower for table in relevant_tables): # change to all ?
                hit_counter += 1
                found_some_table = True
            else:
                miss_counter += 1

            table_index_map = get_table_index(entry)
            gold_tables = get_gold_tables_of_db(entry.get("db_id"), table_index_map)
            print(f"gold tables : {gold_tables}")
            if(check_precision(relevant_tables, gold_tables)):
                precision_amount += 1
                print(f"precision erreicht ")
            if check_recall(relevant_tables, gold_tables):
                recall_amount += 1
                print(f"recall erreicht ")


            """writer.writerow([
                question,
                query,
                found_some_table,
                found_only_relevant_tables,
                found_no_tables,
                relevant_tables,
                method
            ])"""
            #generated_sql_query = get_sql_query(relevant_tables, question)
            #print(f"generated query : {generated_sql_query}")
            #execute_matching_check(entry.get("db_id"), generated_sql_query, gold_query, question)




print(f"hit min one table percentage  {get_percentage(hit_counter)} %")

print(f"miss table percentage {get_percentage(miss_counter)} %")

print(f"no table percentage {get_percentage(no_table_counter)} %")

print(f"precision {get_percentage(precision_amount)} %")

print(f"recall {get_percentage(recall_amount)} %")

"""for index, row in query_question_test_df.iterrows():
    print(f"Zeile {index + 1}:")
    print(f"Query   : {row['query']}")
    print(f"Frage   : {row['question']}\n")
    get_similarity_tables_and_sentence([row['question']], row['question'])"""











