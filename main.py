import json
import math
import os
from pathlib import Path
from data_preprocessing.german_spider_preprocessor import get_english_table_name
from llm_components.gemma.gemma_llm_component import generate_query_by_gemma
from llm_components.groq.groq_llm_componnet import get_generated_sql_queries
from llm_components.ollama.ollama_component import get_query_with_mistral
from schema_linking.custom_auto_link.retrieval_of_faiss_db import get_top_k_columns
from groq import RateLimitError
import re
import time
import ast

from schema_linking.custom_auto_link.vector_db_faiss import embed_documents
from schema_linking.custom_e_sql.get_table_based_value_in_col import get_relevant_c3_tables
from understanding.understanding_components import check_ambiguity_in_question

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import csv
import os
from difflib import SequenceMatcher
from evaluation.eval_spider import check_ea, check_precision, check_recall
from schema_linking.cross_encoder_approach import get_similarity_tables_and_sentence
from structural_linking.gnn_spider_german_or_knowledge_graph import get_gold_tables_of_db, \
    get_all_tables_en, get_relations_per_db, get_relations_per_db_tables

current_path = Path(__file__).resolve()
project_path = str(current_path.parent)
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

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

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

                    ### Stage 1: Extract tables to the question ###

                    relevant_tables, matched_value = get_relevant_c3_tables(" ".join(entry.get('question_toks')))
                    relevant_tables = [table for table in relevant_tables if table != ' ']
                    tmp_similar_tables = []
                    all_tables_en = get_all_tables_en()
                    for table in relevant_tables:
                        tmp_similar_tables.extend(filter_aehnliche_woerter(table, all_tables_en))
                    relevant_tables.extend(tmp_similar_tables)
                    possible_joined_tables = []
                    for table in relevant_tables:
                        possible_joined_tables.extend(get_relations_per_db(table))
                    relevant_tables.extend(possible_joined_tables)
                    relevant_tables = get_top_k_columns(entry.get("question"),5)

                    relevant_tables = [r.get("metadata").get("table") for r in relevant_tables]

                    query = entry.get("query")
                    query_lower = query.lower()
                    table_index_map = get_table_index(entry)
                    gold_tables = get_gold_tables_of_db(entry.get("db_id"), table_index_map)

                    ### Stage 2 : Generate SQL Query ###


                    generated_query = get_query_with_mistral(entry.get("question"),relevant_tables, entry.get("db_id"))
                    generated_query = clean_sql(generated_query)
                    print("generated query")
                    print(generated_query)
                    print("gold query ")
                    print(entry.get("query"))

                    ### Stage 3: Evaluation ###



                    reached = check_ea(generated_query, entry.get("query"), entry.get("db_id"), entry.get("question"))
                    if reached:
                        achieved_ea += 1
                    compare_writer.writerow([entry.get("question"), generated_query,entry.get("query"), reached, False])

                    print(f"current ea {round(achieved_ea / executed_sql_amount * 100, 2)}")

                    if(check_precision(relevant_tables, gold_tables)):
                        precision_amount += 1
                        print(f"precision erreicht ")
                    if check_recall(relevant_tables, gold_tables):
                        recall_amount += 1
                        print(f"recall erreicht ")
                    if not check_precision(relevant_tables, gold_tables) and not check_recall(relevant_tables, gold_tables):
                        print("no recall and no precision")




                    """writer.writerow([
                        question,
                        query,
                        found_some_table,
                        found_only_relevant_tables,
                        found_no_tables,
                        relevant_tables,
                        method
                    ])"""
                    generated_sql_query = get_sql_query(relevant_tables, question)
                    #print(f"generated query : {generated_sql_query}")
                    #execute_matching_check(entry.get("db_id"), generated_sql_query, gold_query, question)
            except RateLimitError as e:
                pass
                error_message = str(e)

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
                compare_writer.writerow([entry.get("question"), generated_query, entry.get("query"), reached, False])

            except Exception as e:
                pass


print(f"hit min one table percentage  {get_percentage(hit_counter)} %")

print(f"miss table percentage {get_percentage(miss_counter)} %")

print(f"no table percentage {get_percentage(no_table_counter)} %")

print(f"precision {get_percentage(precision_amount)} %")

print(f"recall {get_percentage(recall_amount)} %")

print(f"Execution accuracy on all executed queries {round(achieved_ea / executed_sql_amount * 100, 2)}")


















