import os
import sqlite3
from typing import Dict, List
import json
from datasketch import MinHash, MinHashLSH


def get_db_schema_dict() -> Dict[str, List[str]]:
    db_table_map = {}
    db_file_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"
    with open(db_file_path, "r") as db_file:
        db_schema = json.load(db_file)
    for db in db_schema:
        tables = db["table_names"]
        table_idx_col_tuple = db["column_names"]
        for idx, table in enumerate(tables):
            current_columns = []
            for table_idx, col in table_idx_col_tuple:
                if table_idx == idx:
                    current_columns.append(col)
            db_table_map[table] = current_columns
    return db_table_map


def get_db_schema_descriptions():
    db_table_map = {}
    db_file_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"
    descriptions_to_append = []
    with open(db_file_path, "r") as db_file:
        db_schema = json.load(db_file)
    for db in db_schema:
        tables = db["table_names"]
        table_idx_col_tuple = db["column_names"]
        for idx, table in enumerate(tables):
            current_columns = []
            for table_idx, col in table_idx_col_tuple:
                """
                im optimal fall 
                metadata = {
                "table_name": table_name,
                "original_column_name": column_name,
                "column_name": column_info.get('column_name', ''),
                "column_description": column_info.get('column_description', ''),
                "value_description": column_info.get('value_description', '') if kwargs.get("use_value_description", True) else ""
                }
                """
                description = f"""
                Tabelle: {table}
                Spalte: {col}
                """
                descriptions_to_append.append(description)
    return descriptions_to_append

def get_distinct_values_per_col():
    exclude_db_list = [
                "wta_1",
                "formula_1",
                "college_2",
                "sakila_1",
                "flight_4",
                "soccer_1",
                "baseball_1",
                "store_1"
            ]
    db_file_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"
    with open(db_file_path, "r") as db_file:
        db_schema = json.load(db_file)
    all_values_meta_data = []
    for db in db_schema:
        tables = db["table_names_original"]
        columns = db["column_names_original"]
        db_id = db["db_id"]
        if db_id in exclude_db_list:
            continue
        for (table_idx, col) in columns:
            if col == "*":
                continue
            table = tables[table_idx]
            distinct_col_values =  get_column_distinct_column_values(table, col, db_id)

            for val in distinct_col_values:
                all_values_meta_data.append({
                    "table_name": table,
                    "column_name": col,
                    "column_value": val,
                    "db_id": db_id
                })

    return all_values_meta_data


def get_column_distinct_column_values(table_name: str, column_name: str, db_path: str) -> list:
    db_dict = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/spider/database"
    db_file_path = db_dict + "/" + db_path + "/" + f"{db_path}.sqlite"

    fetch_sql = "SELECT DISTINCT `{}` FROM `{}`".format(column_name, table_name)
    try:
        # print(f"db_path: {db_path}")
        conn = sqlite3.connect(db_file_path)
        conn.text_factory = bytes
        c = conn.cursor()
        c.execute(fetch_sql)
        picklist = set()
        for x in c.fetchall():
            if isinstance(x[0], str):
                picklist.add(x[0].encode("utf-8"))
            elif isinstance(x[0], bytes):
                try:
                    picklist.add(x[0].decode("utf-8"))
                except UnicodeDecodeError:
                    picklist.add(x[0].decode("latin-1"))
            else:
                picklist.add(x[0])
        picklist = list(picklist)
    finally:
        conn.close()
    return picklist