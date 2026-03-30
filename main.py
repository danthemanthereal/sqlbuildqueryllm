import json
import os
from pathlib import Path
from data_preprocessing.german_spider_preprocessor import get_english_table_name
from llm_components.gemma.gemma_llm_component import generate_query_by_gemma
from llm_components.ollama.ollama_component import get_query_with_mistral
from schema_linking.custom_auto_link.retrieval_of_faiss_db import get_top_k_columns
from groq import RateLimitError
import re
import time
import ast

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import csv
import os
from difflib import SequenceMatcher
from evaluation.eval_spider import check_ea
from schema_linking.cross_encoder_approach import get_similarity_tables_and_sentence
from structural_linking.gnn_spider_german_or_knowledge_graph import get_gold_tables_of_db, \
    get_all_tables_en, get_relations_per_db, get_relations_per_db_tables

current_path = Path(__file__).resolve()
project_path = str(current_path.parent)

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


#embed_documents(16)
csv_file = project_path + "/output.csv"
missing_csv_file = project_path+ "/missing.csv"
compare_generated_sql_file = project_path+  "/compare_sql_query.csv"
file_exists = os.path.isfile(csv_file)
missing_file_exists = os.path.isfile(missing_csv_file)
compare_file_exists = os.path.isfile(compare_generated_sql_file)
header = ["question", "query", "some_tables_in_query","only_relevant_tables", "no_relevant_tables", "founded_tables", "method"]
header_for_missing_file = ["Frage","Predicted tables Deutsch", "Predicted Tables", "Gold Tables", "Ansatz"]
header_compare_query_file = ["Frage", "Generierte Query", "Gold Query", "EA Reached", "EM Reached"]
with open(csv_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(header)

with open(missing_csv_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not missing_file_exists:
        writer.writerow(header_for_missing_file)

with open(compare_generated_sql_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not compare_file_exists:
        writer.writerow(header_compare_query_file)


method = "cross-encoder"
approach = "auto_link_e5_multilang_small"

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

def clean_sql(text):
    text = text.strip()

    match = re.search(r"```sql\s*(.*?)```", text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()

    return text

def extract_error_dict(error_text: str):

    match = re.search(r"\{.*\}", error_text, re.DOTALL)

    if match:
        return ast.literal_eval(match.group())

    return None


json_file = project_path + "/data/dataset_spider_de/multispider/with_original_value/dev_de.json"
hit_counter = 0
miss_counter = 0
no_table_counter = 0
precision_amount = 0
recall_amount = 0
executed_sql_amount = 0
achieved_ea = 0


#embed_documents(16)
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

#splits = get_all_splitted_german_spider()
#data = splits[0]


with open(compare_generated_sql_file, "a", newline="", encoding="utf-8") as f:
    missing_writer = csv.writer(f)
    compare_writer = csv.writer(f)

    for i, entry in enumerate(data):
            try:
                print("f current round ", executed_sql_amount)
                executed_sql_amount += 1
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
                    german_prediction = relevant_tables
                    #relevant_tables = [r.get("metadata").get("table") for r in relevant_tables]
                    #relevant_tables = [dict.get("metadata", {}).get("table", " ") for dict in r]
                    relevant_tables = list(dict.fromkeys(relevant_tables))
                    #print("predicted_tables in deutsch: ", relevant_tables)
                    #relevant_tables = [get_english_table_name(table) for table in relevant_tables]
                    flattened_tables = []

                    for table in relevant_tables:
                        flattened_tables.extend(get_english_table_name(table))

                    relevant_tables = flattened_tables
                    # similar schreibweise noch hinzu
                    similar_words = []
                    englisch_tables_name = get_all_tables_en()
                    for table in relevant_tables:
                        sim_words = filter_aehnliche_woerter(table, englisch_tables_name, 0.8)
                        similar_words.extend(sim_words)

                    relevant_tables.extend(similar_words)

                    # with help of db values
                   # tables_with_db_values = get_relevant_tables_of_question(entry.get("question"))
                   # relevant_tables.extend(tables_with_db_values)
                    #relevant_tables = list(dict.fromkeys(relevant_tables))

                    joined_tables = []
                    for table in relevant_tables:
                        joined_tables.extend(get_relations_per_db_tables(table))
                    relevant_tables.extend(joined_tables)
                    #relevant_tables = list(dict.fromkeys(relevant_tables))


                   # print(f"predicted tables : {relevant_tables}")
                   # print(f"matched values : {matched_value}")
                    query = entry.get("query")
                    query_lower = query.lower()
                    table_index_map = get_table_index(entry)
                    gold_tables = get_gold_tables_of_db(entry.get("db_id"), table_index_map)

                    # execute sql query based on predicted tables
                    generated_query = get_query_with_mistral(entry.get("question"),relevant_tables, entry.get("db_id"))
                    generated_query = clean_sql(generated_query)
                    print("generated query")
                    print(generated_query)
                    print("gold query ")
                    print(entry.get("query"))

                    #check ea reached for this question

                    reached = check_ea(generated_query, entry.get("query"), entry.get("db_id"))
                    if reached:
                        achieved_ea += 1
                    compare_writer.writerow([entry.get("question"), generated_query,entry.get("query"), reached, False])

                    print(f"current ea {round(achieved_ea / executed_sql_amount * 100, 2)}")
                    """print(f"gold tables : {gold_tables}")
                   # print("query ", entry.get("query"))
                    if not relevant_tables:
                        no_table_counter += 1
                        found_no_tables = True
                        continue
    
                    if any(table.lower() in query_lower for table in relevant_tables): # change to all ?
                        hit_counter += 1
                        found_some_table = True
                    else:
    
                        missing_writer.writerow([entry.get("question"), german_prediction,relevant_tables, gold_tables, approach])
                        miss_counter += 1


                    if(check_precision(relevant_tables, gold_tables)):
                        precision_amount += 1
                        print(f"precision erreicht ")
                    if check_recall(relevant_tables, gold_tables):
                        recall_amount += 1
                        print(f"recall erreicht ")
                    if not check_precision(relevant_tables, gold_tables) and not check_recall(relevant_tables, gold_tables):
                        print("no recall and no precision")
                        missing_writer.writerow([entry.get("question"), german_prediction,relevant_tables, gold_tables, approach])"""




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
            except RateLimitError as e:
                pass
                """error_message = str(e)

                match = re.search(
                    r"try again in\s*(?:(\d+)m)?\s*(?:(\d+(?:\.\d+)?)s)?",
                    error_message,
                )

                retry_after = 60
                if match:
                    minutes = int(match.group(1)) if match.group(1) else 0
                    seconds = float(match.group(2)) if match.group(2) else 0.0

                    retry_after = math.ceil(minutes * 60 + seconds)

                retry_after += 1

                time.sleep(retry_after)

                # generate query after 429 error
                print("Nochmal ausführen nach 429 Rate Limit ")
                generated_query = get_generated_sql_queries(entry.get("question"), relevant_tables, 2)
                generated_query = clean_sql(generated_query)
                print("generated query")
                print(generated_query)
                print("gold query ")
                print(entry.get("query"))

                # check ea reached for this question

                reached = check_ea(generated_query, entry.get("query"), entry.get("db_id"))
                if reached:
                    achieved_ea += 1
                executed_sql_amount += 1
                compare_writer.writerow([entry.get("question"), generated_query, entry.get("query"), reached, False])"""

            except Exception as e:
                try:
                    print("in exception ")
                    print(e)
                    error_dict = extract_error_dict(str(e))
                    if error_dict:
                        retry_info = error_dict['error']['details'][-1]


                        delay_str = retry_info.get('retryDelay', None)
                        if delay_str:
                            print(f"nach delay ")
                            delay_seconds = float(delay_str.replace('s', ''))
                            delay_seconds+= 1
                            time.sleep(delay_seconds)
                            generated_query = generate_query_by_gemma(entry.get("question"), relevant_tables)
                            generated_query = clean_sql(generated_query)
                            print("generated query")
                            print(generated_query)
                            print("gold query ")
                            print(entry.get("query"))

                            # check ea reached for this question

                            reached = check_ea(generated_query, entry.get("query"), entry.get("db_id"))
                            if reached:
                                achieved_ea += 1
                            compare_writer.writerow(
                                [entry.get("question"), generated_query, entry.get("query"), reached, False])
                except Exception as e:
                    print("ex in try ctahc")
                    print(e)

#compare_writer.writerow([entry.get("question"), generated_query, entry.get("query"), False, e])

#print(f"hit min one table percentage  {get_percentage(hit_counter)} %")

#print(f"miss table percentage {get_percentage(miss_counter)} %")

#print(f"no table percentage {get_percentage(no_table_counter)} %")

#print(f"precision {get_percentage(precision_amount)} %")

#print(f"recall {get_percentage(recall_amount)} %")

print(f"Execution accuracy on all executed queries {round(achieved_ea / executed_sql_amount * 100, 2)}")

"""for index, row in query_question_test_df.iterrows():
    print(f"Zeile {index + 1}:")
    print(f"Query   : {row['query']}")
    print(f"Frage   : {row['question']}\n")
    get_similarity_tables_and_sentence([row['question']], row['question'])"""


















