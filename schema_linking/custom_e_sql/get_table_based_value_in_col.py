import json
import random
import sqlite3
from collections import defaultdict
from typing import Union, Any
from pathlib import Path

def get_table_column_map():
    schema_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        databases = json.load(f)

    table_col_map = {}

    for db in databases:
        table_names = db["table_names"]
        column_names = db["column_names"]

        schema = defaultdict(list)

        for table_idx, column_name in column_names:
            if table_idx == -1:
                continue
            table_name = table_names[table_idx]
            schema[table_name].append(column_name)

        for table, columns in schema.items():
           table_col_map[table] = columns

    return table_col_map


def execute_sql(db_path: str, sql: str, fetch: Union[str, int] = "all") -> Any:
    """
    Executes an SQL query on a database and fetches results.

    Arguments:
        db_path (str): The database sqlite file path.
        sql (str): The SQL query to execute.
        fetch (Union[str, int]): How to fetch the results. Options are "all", "one", "random", or an integer.

    Returns:
        resutls: SQL execution results .
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            if fetch == "all":
                return cursor.fetchall()
            elif fetch == "one":
                return cursor.fetchone()
            elif fetch == "random":
                samples = cursor.fetchmany(10)
                return random.choice(samples) if samples else []
            elif isinstance(fetch, int):
                return cursor.fetchmany(fetch)
            else:
                raise ValueError("Invalid fetch argument. Must be 'all', 'one', 'random', or an integer.")
    except Exception as e:

        raise e

def go_all_dbs():
    current_path = Path(__file__).resolve()
    project_path = current_path.parent.parent
    data_base_path = project_path / "data" / "dataset_spider_de" / "spider" / "database"
    for f in data_base_path.iterdir():
        sql_lite_path = data_base_path / f.name / f"{f.name}.sqlite"





def get_distinct_val_of_columns(db_path: str, table: str, column: str):
    sql = f"SELECT DISTINCT `{column}` FROM `{table}`"

    query_result = execute_sql(db_path, sql)