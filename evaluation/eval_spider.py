from pathlib import Path
import sqlite3
import csv
import re

from llm_components.ollama.ollama_component import return_corrected_sql, return_corrected_sql_wrapper


def execute_matching_check(db_file, generated_query, gold_query, question):
    current_path = Path(__file__).resolve()
    project_path = current_path.parent

    spider_data_dict_path = project_path / "data" / "dataset_spider_de" / "spider" / "database"

    sqlite_file_path = spider_data_dict_path / db_file / f"{db_file}.sqlite"

    result_gold_query = execute_sql(sqlite_file_path, gold_query)



    correct = 0
    total = len(result_gold_query)
    output_csv = "execution_results.csv"

    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "question",
            "generated_query",
            "gold_query",
            "is_correct"
        ])

    for gold, pred in zip(gold_query, generated_query):
        gold_res = execute_sql(sqlite_file_path, gold)
        pred_res = execute_sql(sqlite_file_path, pred)

        if gold_res is None or pred_res is None:
            continue

        is_correct = False
        if sorted(gold_res) == sorted(pred_res):
            correct += 1
            is_correct = True

        writer.writerow([
            question,
            pred,
            gold,
            is_correct
        ])

    return correct / total

def execute_sql(db_path, sql):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    except Exception as e:
        result = None
    conn.close()
    return result

def check_precision(generated_tables, gold_tables) -> bool:
    return set(generated_tables) == set(gold_tables)


def check_recall(generated_tables, gold_tables) -> bool:
    return  set(gold_tables) <= set(generated_tables)


# gleiche ergebnisse ? 
def check_ea(generated_query, gold_query, db_id, question) -> bool:
    try:
        current_path = Path(__file__).resolve()
        project_path = str(current_path.parent.parent)
        db_path = project_path + "/data/dataset_spider_de/spider/database" + f"/{db_id}/{db_id}.sqlite"
        conn = sqlite3.connect(db_path)

        cursor = conn.cursor()
        cursor.execute(generated_query)
        predicted_res = cursor.fetchall()
        cursor.execute(gold_query)
        ground_truth_res = cursor.fetchall()

        if set(predicted_res) == set(ground_truth_res):
            return True
        return False
    except Exception as e:
        print("Fehler in db ausführen ")
        print(e)
        return False
        


def clean_sql(text):
    text = text.strip()

    match = re.search(r"```sql\s*(.*?)```", text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()

    return text