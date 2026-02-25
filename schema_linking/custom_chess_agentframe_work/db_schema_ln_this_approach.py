import os
from typing import Dict, List
import json


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