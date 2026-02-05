from pathlib import Path
import sqlite3

def execute_matching_check(db_file, generated_query, gold_query):
    current_path = Path(__file__).resolve()
    project_path = current_path.parent

    spider_data_dict_path = project_path / "data" / "dataset_spider_de" / "spider" / "database"

    sqlite_file_path = spider_data_dict_path / db_file / f"{db_file}.sqlite"

    result_from_generated_query = []#execute_sql(sqlite_file_path, generated_query)
    result_gold_query = execute_sql(sqlite_file_path, gold_query)



    correct = 0
    total = len(result_gold_query)

    for gold, pred in zip(gold_query, generated_query):
        gold_res = execute_sql(sqlite_file_path, gold)
        pred_res = execute_sql(sqlite_file_path, pred)

        if gold_res is None or pred_res is None:
            continue  # runtime error → falsch

        # Reihenfolge ignorieren
        if sorted(gold_res) == sorted(pred_res):
            correct += 1

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