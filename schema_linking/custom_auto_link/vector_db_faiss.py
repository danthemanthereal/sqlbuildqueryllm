import sqlite3
import numpy as np
import faiss
faiss.omp_set_num_threads(1)
import os
import json
from sentence_transformers import SentenceTransformer
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def embed_documents(batch_size: int = 32):
    model = SentenceTransformer('intfloat/e5-small-v2')

    log = {}
    db_dict_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/spider/database"
    json_file = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"
    with open(json_file, "r", encoding="utf-8") as f:
        db_schemas = json.load(f)

    for db in db_schemas:
        db_id = db["db_id"]
        tables = db["table_names"]
        columns = db["column_names"]
        column_types = db["column_types"]
        all_descriptions = []
        metadata_mapping = []
        idx_col = 0
        embedd_fais_dict_path = f"/Users/danielschmidt/Desktop/sqlbuildqueryllm/schema_linking/custom_auto_link/embedded_documents/{db_id}"

        for ind, (table_ind, col_name) in enumerate(columns):
            col_info = dict()
            col_info["column_name"] = col_name
            table_name = tables[table_ind]
            column_data_type = column_types[idx_col]
            description = (f"Tablle: {table_name}"
                           f"Spalte: {col_name}"
                           f"Datentyp: {column_data_type}")
            all_descriptions.append(description)
            distinct_values_of_current_col = []
            invalid_dbs = [
                "wta_1",
                "formula_1",
                "college_2",
                "sakila_1",
                "flight_4",
                "soccer_1",
                "baseball_1",
                "store_1"
            ]
            if db_id not in invalid_dbs:
                pass
                #distinct_values_of_current_col = get_column_distinct_column_values(table_name, col_name, db_id)
            metadata_mapping.append({
                "table": table_name,
                "column": col_name,
                "column_type": column_data_type,
               # "column_value": distinct_values_of_current_col,

            })
            idx_col += 1

        db_embeddings = []
        for i in range(0, len(all_descriptions), batch_size):
            batch_descriptions = all_descriptions[i:i + batch_size]
            batch_embeddings = model.encode(batch_descriptions, convert_to_numpy=True)
            db_embeddings.extend(batch_embeddings)

        dimension = len(db_embeddings[0])
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(db_embeddings, dtype=np.float32))
        os.makedirs(embedd_fais_dict_path, exist_ok=True)
        faiss.write_index(index, os.path.join(embedd_fais_dict_path, "index.faiss"))

        with open(os.path.join(embedd_fais_dict_path, "metadata.json"), "w", encoding="utf-8") as f_meta:
            json.dump(metadata_mapping, f_meta, ensure_ascii=False, indent=2)


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
