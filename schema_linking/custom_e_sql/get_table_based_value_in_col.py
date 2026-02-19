import json
import random
import sqlite3
from collections import defaultdict
from typing import Union, Any
from pathlib import Path
from rank_bm25 import BM25Okapi
from rapidfuzz import fuzz, process

from structural_linking.gnn_spider_german_or_knowledge_graph import get_all_tables_en


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

def get_table_column_map_per_db_id():
    schema_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        databases = json.load(f)

    table_col_map_per_db_id = {}

    for db in databases:
        table_names = db["table_names_original"]
        column_names = db["column_names_original"]
        db_id = db["db_id"]

        schema = defaultdict(list)

        for table_idx, column_name in column_names:
            if table_idx == -1:
                continue
            table_name = table_names[table_idx]
            schema[table_name].append(column_name)

        table_col_map = {}
        for table, columns in schema.items():
           table_col_map[table] = columns

        if db_id in table_col_map_per_db_id:
            table_col_map_per_db_id[db_id].append(table_col_map)
        else:
            table_col_map_per_db_id[db_id] = [table_col_map]

    return table_col_map_per_db_id


def get_table_column_map_per_db_id_german():
    schema_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        databases = json.load(f)

    table_col_map_per_db_id = {}

    for db in databases:
        table_names = db["table_names"]
        column_names = db["column_names"]
        db_id = db["db_id"]

        schema = defaultdict(list)

        for table_idx, column_name in column_names:
            if table_idx == -1:
                continue
            table_name = table_names[table_idx]
            schema[table_name].append(column_name)

        table_col_map = {}
        for table, columns in schema.items():
           table_col_map[table] = columns

        if db_id in table_col_map_per_db_id:
            table_col_map_per_db_id[db_id].append(table_col_map)
        else:
            table_col_map_per_db_id[db_id] = [table_col_map]

    return table_col_map_per_db_id


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
    db_table_col_map = get_table_column_map_per_db_id()
    current_path = Path(__file__).resolve()
    project_path = current_path.parent.parent.parent
    data_base_path = project_path / "data" / "dataset_spider_de" / "spider" / "database"
    for f in data_base_path.iterdir():
        sql_lite_path = data_base_path / f.name / f"{f.name}.sqlite"
        if (f.name == "bike_1" or
                f.name == "wta_1" or
                f.name == "formula_1" or
                f.name == "college_2" or
                f.name == "sakila_1" or
                f.name == "flight_4" or
                f.name == "soccer_1" or
                f.name == "baseball_1" or
            f.name == "store_1"

        ):
            continue
        sql_lite_path_str = str(sql_lite_path)
        all_table_cols_of_db = db_table_col_map[f.name]

        for table_col_map in all_table_cols_of_db:
            for key, value in table_col_map.items():
                table = key
                columns = value
                for column in columns:
                    print(sql_lite_path_str)
                    get_distinct_val_of_columns(sql_lite_path_str, table, column)

def get_distinct_val_of_columns(db_path: str, table: str, column: str):
    sql = f"SELECT DISTINCT `{column}` FROM `{table}`"

    query_result = execute_sql(db_path, sql)


def construct_tokenized_db_table_value_corpus():

    # generating corpus whose items are tokenized version of "table_name column_name value" for each value and table in the database.
    corpus = []
    db_corpus = []

    # with my db schema
    db_table_col_map = get_table_column_map_per_db_id()
    db_table_col_map_german = get_table_column_map_per_db_id_german()
    current_path = Path(__file__).resolve()
    project_path = current_path.parent.parent.parent
    data_base_path = project_path / "data" / "dataset_spider_de" / "spider" / "database"
    for f in data_base_path.iterdir():
        sql_lite_path = data_base_path / f.name / f"{f.name}.sqlite"
        if (f.name == "bike_1" or
                f.name == "wta_1" or
                f.name == "formula_1" or
                f.name == "college_2" or
                f.name == "sakila_1" or
                f.name == "flight_4" or
                f.name == "soccer_1" or
                f.name == "baseball_1" or
                f.name == "store_1"

        ):
            continue
        sql_lite_path_str = str(sql_lite_path)
        all_table_cols_of_db = db_table_col_map[f.name]
        all_table_cols_of_db_german = db_table_col_map_german[f.name]

        for idx, table_col_map in enumerate(all_table_cols_of_db):
            current_table_col_map_german = all_table_cols_of_db_german[idx]

            for (eng_table, eng_columns), (ger_table, ger_columns) in zip(
                    table_col_map.items(),
                    current_table_col_map_german.items()
            ):

                for eng_column, ger_column in zip(eng_columns, ger_columns):

                    col_distinct_values = execute_sql(
                        sql_lite_path_str,
                        f"SELECT DISTINCT `{eng_column}` FROM `{eng_table}`"
                    )

                    col_distinct_values = [
                        str(value_tuple[0])
                        for value_tuple in col_distinct_values
                        if value_tuple[0]
                    ]

                    if len(col_distinct_values) > 0:
                        average_length = sum(len(v) for v in col_distinct_values) / len(col_distinct_values)
                    else:
                        average_length = 0

                    if average_length > 600:
                        col_distinct_values = [col_distinct_values[0]]

                    table_col_value_str = [
                        f"{ger_table} {ger_column} {val}"
                        for val in col_distinct_values
                    ]
                    corpus.extend(table_col_value_str)

                    table_col_value_tuples = [
                        (eng_table, eng_column, val)
                        for val in col_distinct_values
                    ]
                    db_corpus.extend(table_col_value_tuples)

    tokenized_db_corpus = [doc.split(" ") for doc in corpus]
    # tokenized_db_corpus = [word_tokenize(doc) for doc in corpus if doc]  # takes too much time, so don't use it
    return tokenized_db_corpus, db_corpus

def get_relevant_tables_of_question(question: str):
    tokenized_db_corpus, db_corpuse = construct_tokenized_db_table_value_corpus()
    bm25 = BM25Okapi(tokenized_db_corpus)

    tokenized_query = question.split(" ")
    scores = bm25.get_scores(tokenized_query)

    import numpy as np

    top_k = 5
    top_indices = np.argsort(scores)[::-1][:top_k]

    tables = []
    for idx in top_indices:
        table, column, value = db_corpuse[idx]
        tables.append(table)

    tokenized_values_only, tokenized_values_col, db_corpus = build_corpora()
    results_values_only = retrieve(question, tokenized_values_only, db_corpus, top_k=5)
    results_values_col = retrieve(question, tokenized_values_col, db_corpus, top_k=5)
    tables.extend(results_values_only)
    tables.extend(results_values_col)

    # get tables which writes similar
    tables = list(dict.fromkeys(tables))
    all_db_tables = get_all_tables_en()
    simililar_tables_based_on_found = []
    for table in tables:
        similar_tables_raw = process.extract(
            question,
            all_db_tables,
            scorer=fuzz.ratio,
            score_cutoff=80
        )
        similar_tables = [candidate for candidate, score, idx in similar_tables_raw]
        simililar_tables_based_on_found.extend(similar_tables)
    return tables.extend(simililar_tables_based_on_found)



def build_corpora():
    """
    Baut zwei parallele Korpora:
    - values_only_corpus: nur die Werte (für values-only Retrieval)
    - values_col_corpus: Werte + Spaltenname (für values+column Retrieval)
    db_corpus: parallele Liste (table, column, value)
    """
    values_only_corpus = []
    values_col_corpus = []
    db_corpus = []

    db_table_col_map = get_table_column_map_per_db_id()
    db_table_col_map_german = get_table_column_map_per_db_id_german()
    current_path = Path(__file__).resolve()
    project_path = current_path.parent.parent.parent
    data_base_path = project_path / "data" / "dataset_spider_de" / "spider" / "database"
    for f in data_base_path.iterdir():
        sql_lite_path = data_base_path / f.name / f"{f.name}.sqlite"
        if (f.name == "bike_1" or
                f.name == "wta_1" or
                f.name == "formula_1" or
                f.name == "college_2" or
                f.name == "sakila_1" or
                f.name == "flight_4" or
                f.name == "soccer_1" or
                f.name == "baseball_1" or
                f.name == "store_1"

        ):
            continue
        sql_lite_path_str = str(sql_lite_path)
        all_table_cols_of_db = db_table_col_map[f.name]
        all_table_cols_of_db_german = db_table_col_map_german[f.name]

        for idx, table_col_map in enumerate(all_table_cols_of_db):
            current_table_col_map_german = all_table_cols_of_db_german[idx]

            for (eng_table, eng_columns), (ger_table, ger_columns) in zip(
                    table_col_map.items(),
                    current_table_col_map_german.items()
            ):

                for eng_column, ger_column in zip(eng_columns, ger_columns):
                    values = execute_sql(
                        sql_lite_path_str,
                        f"SELECT DISTINCT `{eng_column}` FROM `{eng_table}`"
                    )

                    values = [str(v[0]) for v in values if v[0] is not None]

                    if len(values) > 0:
                        avg_len = sum(len(v) for v in values) / len(values)
                        if avg_len > 600:
                            values = [values[0]]

                    for val in values:
                        values_only_corpus.append(val.lower())

                        values_col_corpus.append(f"{ger_column.lower()} {val.lower()}")

                        db_corpus.append((ger_table, ger_column, val))



    tokenized_values_only = [v.split() for v in values_only_corpus]
    tokenized_values_col = [v.split() for v in values_col_corpus]

    return tokenized_values_only, tokenized_values_col, db_corpus

def retrieve(query, tokenized_corpus, db_corpus, top_k=5):
    """
    Allgemeine Retrieval-Funktion:
    - tokenized_corpus: BM25 Tokenized Corpus
    - db_corpus: parallele Liste (table, column, value)
    """
    bm25 = BM25Okapi(tokenized_corpus)
    import re
    import numpy as np
    # Query Tokenization: nur Wörter/Zahlen
    query_tokens = re.findall(r'\w+', query.lower())

    scores = bm25.get_scores(query_tokens)
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    tables = []
    for idx in top_indices:
        table, column, value = db_corpus[idx]
        tables.append(table)
    return tables
