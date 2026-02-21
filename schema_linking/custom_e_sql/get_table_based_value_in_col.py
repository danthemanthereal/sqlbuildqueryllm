import json
import random
import difflib
import sqlite3
from collections import defaultdict
from typing import Union, Any, List, Optional, Tuple
from pathlib import Path
from rank_bm25 import BM25Okapi
from rapidfuzz import fuzz, process

from structural_linking.gnn_spider_german_or_knowledge_graph import get_all_tables_en


_stopwords = {
    'aber', 'alle', 'allem', 'allen', 'aller', 'alles', 'als', 'also', 'am',
    'an', 'ander', 'andere', 'anderem', 'anderen', 'anderer', 'anderes',
    'anderm', 'andern', 'anderr', 'anders', 'auch', 'auf', 'aus', 'bei',
    'bin', 'bis', 'bist', 'da', 'damit', 'dann', 'der', 'den', 'des',
    'dem', 'die', 'das', 'dass', 'daß', 'derselbe', 'derselben',
    'denselben', 'desselben', 'demselben', 'dieselbe', 'dieselben',
    'dasselbe', 'dazu', 'dein', 'deine', 'deinem', 'deinen', 'deiner',
    'deines', 'denn', 'derer', 'dessen', 'dich', 'dir', 'du', 'dies',
    'diese', 'diesem', 'diesen', 'dieser', 'dieses', 'doch', 'dort',
    'durch', 'ein', 'eine', 'einem', 'einen', 'einer', 'eines',
    'einig', 'einige', 'einigem', 'einigen', 'einiger', 'einiges',
    'einmal', 'er', 'ihn', 'ihm', 'es', 'etwas', 'euer', 'eure',
    'eurem', 'euren', 'eurer', 'eures', 'für', 'gegen', 'gewesen',
    'hab', 'habe', 'haben', 'hat', 'hatte', 'hatten', 'hier',
    'hin', 'hinter', 'ich', 'mich', 'mir', 'ihr', 'ihre',
    'ihrem', 'ihren', 'ihrer', 'ihres', 'euch', 'im', 'in',
    'indem', 'ins', 'ist', 'jede', 'jedem', 'jeden', 'jeder',
    'jedes', 'jene', 'jenem', 'jenen', 'jener', 'jenes',
    'jetzt', 'kann', 'kein', 'keine', 'keinem', 'keinen',
    'keiner', 'keines', 'können', 'könnte', 'machen',
    'man', 'manche', 'manchem', 'manchen', 'mancher',
    'manches', 'mein', 'meine', 'meinem', 'meinen',
    'meiner', 'meines', 'mit', 'muss', 'musste',
    'nach', 'nicht', 'nichts', 'noch', 'nun', 'nur',
    'ob', 'oder', 'ohne', 'sehr', 'sein', 'seine',
    'seinem', 'seinen', 'seiner', 'seines', 'selbst',
    'sich', 'sie', 'ihnen', 'sind', 'so', 'solche',
    'solchem', 'solchen', 'solcher', 'solches',
    'soll', 'sollte', 'sondern', 'sonst', 'über',
    'um', 'und', 'uns', 'unser', 'unserem', 'unseren',
    'unserer', 'unseres', 'unter', 'viel', 'vom',
    'von', 'vor', 'während', 'war', 'waren',
    'warst', 'was', 'weg', 'weil', 'weiter',
    'welche', 'welchem', 'welchen', 'welcher',
    'welches', 'wenn', 'werde', 'werden',
    'wie', 'wieder', 'will', 'wir', 'wird',
    'wirst', 'wo', 'wollen', 'wollte',
    'würde', 'würden', 'zu', 'zum', 'zur',
    'zwar', 'zwischen'
}

_commonwords = {"nein", "viele", "ja"}

class Match(object):
    def __init__(self, start: int, size: int) -> None:
        self.start = start
        self.size = size


def is_span_separator(c: str) -> bool:
    return c in "'\"()`,.?! "

def get_effective_match_source(s: str, start: int, end: int) -> Match:
    _start = -1

    for i in range(start, start - 2, -1):
        if i < 0:
            _start = i + 1
            break
        if is_span_separator(s[i]):
            _start = i
            break

    if _start < 0:
        return None

    _end = -1
    for i in range(end - 1, end + 3):
        if i >= len(s):
            _end = i - 1
            break
        if is_span_separator(s[i]):
            _end = i
            break

    if _end < 0:
        return None

    while _start < len(s) and is_span_separator(s[_start]):
        _start += 1
    while _end >= 0 and is_span_separator(s[_end]):
        _end -= 1

    return Match(_start, _end - _start + 1)

def is_number(s: str) -> bool:
    try:
        float(s.replace(",", ""))
        return True
    except:
        return False


def is_stopword(s: str) -> bool:
    return s.strip() in _stopwords


def is_commonword(s: str) -> bool:
    return s.strip() in _commonwords


def is_common_db_term(s: str) -> bool:
    return s.strip() in ["id"]

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
            table,
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

def get_relevant_c3_tables(question: str):
    db_table_col_map = get_table_column_map_per_db_id()
    db_table_col_map_german = get_table_column_map_per_db_id_german()
    current_path = Path(__file__).resolve()
    project_path = current_path.parent.parent.parent
    data_base_path = project_path / "data" / "dataset_spider_de" / "spider" / "database"
    matched_tables = []
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


        for idx, table_col_map in enumerate(all_table_cols_of_db):
            for (table_name, columns) in table_col_map.items():
                for column_name in columns:
                    picklist = get_column_picklist(
                        table_name=table_name, column_name=column_name, db_path=sql_lite_path_str
                    )
                    # only maintain data in ``str'' type
                    picklist = [ele.strip() for ele in picklist if isinstance(ele, str)]
                    # picklist is unordered, we sort it to ensure the reproduction stability
                    picklist = sorted(picklist)
                    matches = []
                    if picklist and isinstance(picklist[0], str):
                        matched_entries = get_matched_entries(
                            s=question,
                            field_values=picklist,
                            m_theta=0.85,
                            s_theta=0.85,
                        )

                        if matched_entries:
                            num_values_inserted = 0
                            for _match_str, (
                                    field_value,
                                    _s_match_str,
                                    match_score,
                                    s_match_score,
                                    _match_size,
                            ) in matched_entries:
                                if "name" in column_name and match_score * s_match_score < 1:
                                    continue
                                if table_name != "sqlite_sequence":  # Spider database artifact
                                    matches.append(field_value.strip())
                                    num_values_inserted += 1
                                    matched_tables.append(table_name)
                                    if num_values_inserted >= 2:
                                        break

    return matched_tables


def get_column_picklist(table_name: str, column_name: str, db_path: str) -> list:
    fetch_sql = "SELECT DISTINCT `{}` FROM `{}`".format(column_name, table_name)
    try:
        # print(f"db_path: {db_path}")
        conn = sqlite3.connect(db_path)
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


def split(s: str) -> List[str]:
    return [c.lower() for c in s.strip()]


def get_matched_entries(
        s: str, field_values: List[str], m_theta: float = 0.85, s_theta: float = 0.85
) -> Optional[List[Tuple[str, Tuple[str, str, float, float, int]]]]:
    if not field_values:
        return None

    if isinstance(s, str):
        n_grams = split(s)
    else:
        n_grams = s

    matched = dict()
    for field_value in field_values:
        if not isinstance(field_value, str):
            continue
        fv_tokens = split(field_value)
        sm = difflib.SequenceMatcher(None, n_grams, fv_tokens)
        match = sm.find_longest_match(0, len(n_grams), 0, len(fv_tokens))
        if match.size > 0:
            source_match = get_effective_match_source(
                n_grams, match.a, match.a + match.size
            )
            if source_match and source_match.size > 1:
                match_str = field_value[match.b: match.b + match.size]
                source_match_str = s[
                                   source_match.start: source_match.start + source_match.size
                                   ]
                c_match_str = match_str.lower().strip()
                c_source_match_str = source_match_str.lower().strip()
                c_field_value = field_value.lower().strip()
                if (
                        c_match_str
                        and not is_number(c_match_str)
                        and not is_common_db_term(c_match_str)
                ):
                    if (
                            is_stopword(c_match_str)
                            or is_stopword(c_source_match_str)
                            or is_stopword(c_field_value)
                    ):
                        continue
                    if c_source_match_str.endswith(c_match_str + "'s"):
                        match_score = 1.0
                    else:
                        if prefix_match(c_field_value, c_source_match_str):
                            match_score = (
                                    fuzz.ratio(c_field_value, c_source_match_str) / 100
                            )
                        else:
                            match_score = 0
                    if (
                            is_commonword(c_match_str)
                            or is_commonword(c_source_match_str)
                            or is_commonword(c_field_value)
                    ) and match_score < 1:
                        continue
                    s_match_score = match_score
                    if match_score >= m_theta and s_match_score >= s_theta:
                        if field_value.isupper() and match_score * s_match_score < 1:
                            continue
                        matched[match_str] = (
                            field_value,
                            source_match_str,
                            match_score,
                            s_match_score,
                            match.size,
                        )

    if not matched:
        return None
    else:
        return sorted(
            matched.items(),
            key=lambda x: (1e16 * x[1][2] + 1e8 * x[1][3] + x[1][4]),
            reverse=True,
        )

def prefix_match(s1: str, s2: str) -> bool:
    i, j = 0, 0
    for i in range(len(s1)):
        if not is_span_separator(s1[i]):
            break
    for j in range(len(s2)):
        if not is_span_separator(s2[j]):
            break
    if i < len(s1) and j < len(s2):
        return s1[i] == s2[j]
    elif i >= len(s1) and j >= len(s2):
        return True
    else:
        return False
