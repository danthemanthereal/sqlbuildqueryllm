import sqlite3
import numpy as np
import faiss

faiss.omp_set_num_threads(1)
import os
import json
from sentence_transformers import SentenceTransformer

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def embed_documents(batch_size: int = 32):
    model = SentenceTransformer('intfloat/multilingual-e5-small')

    log = {}
    db_dict_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/spider/database"
    json_file = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/table_map_with_desc.json"
    with open(json_file, 'r', encoding='utf-8') as f:
        all_table_map = json.load(f)
    description_to_embedd = {}
    meta_data_to_embedd = {}
    for table in all_table_map:
        table_name = table["table_name"]
        table_description = table["table_description"]
        columns = table["column_names"]
        columns_description = table["column_descriptions"]
        db_id = table["db_id"]
        for idx, col in enumerate(columns):
            current_description = columns_description[idx]
            current_descriptions_to_embed = f"""
                Tabelle : {table_name}
                Beschreibung der Tabelle : {table_description}
                Spalte : {col}
                Beschreibung der Spalte : {current_description}
            """
            current_meta_data = {
                "table": table_name,
                "table_description": table_description,
                "column": col,
                "column_description": current_description,
            }
            if db_id in description_to_embedd:
                description_to_embedd[db_id].append(current_descriptions_to_embed)
            else:
                description_to_embedd[db_id] = [current_descriptions_to_embed]

            if db_id in meta_data_to_embedd:
                meta_data_to_embedd[db_id].append(current_meta_data)
            else:
                meta_data_to_embedd[db_id] = [current_meta_data]

    for key in description_to_embedd.keys():
        all_descriptions = description_to_embedd[key]
        metadata_mapping = meta_data_to_embedd[key]
        db_embeddings = []
        embedd_fais_dict_path = f"/Users/danielschmidt/Desktop/sqlbuildqueryllm/schema_linking/custom_auto_link/embedded_documents/{key}"
        for i in range(0, len(all_descriptions), batch_size):
            batch_descriptions = all_descriptions[i:i + batch_size]
            batch_embeddings = model.encode(
                batch_descriptions,
                convert_to_numpy=True,
                batch_size=batch_size,
                device="cpu", )
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


"""with open(json_file, "r", encoding="utf-8") as f:
    db_schemas = json.load(f)

for db in db_schemas:
    db_id = db["db_id"]
    tables = db["table_names"]
    columns = db["column_names"]
    column_types = db["column_types"]
    original_tables = db["table_names_original"]
    original_columns = db["column_names_original"]
    all_descriptions = []
    metadata_mapping = []
    idx_col = 0
    embedd_fais_dict_path = f"/Users/danielschmidt/Desktop/sqlbuildqueryllm/schema_linking/custom_auto_link/embedded_documents/{db_id}"

    for ind, (table_ind, col_name) in enumerate(columns):
        if col_name == "*":
            continue
        col_info = dict()
        col_info["column_name"] = col_name
        table_name = tables[table_ind]
        english_col_tupel = original_columns[ind]
        english_table_id = english_col_tupel[0]
        english_table = original_tables[english_table_id]
        english_col_name = english_col_tupel[1]
        column_data_type = column_types[idx_col]
        column_values = []
        no_file_exists = [
            "bike_1",
            "wta_1",
            "formula_1",
            "college_2",
            "sakila_1",
            "flight_4",
            "soccer_1",
            "baseball_1",
            "store_1"
        ]
        if db_id not in no_file_exists:
            pass
          ##  column_values = get_column_distinct_column_values(english_table,
            #                                                  english_col_name,
             #                                                 db_id)

        description = (f"Tabelle: {table_name}\n"
                       f"Spalte: {col_name}\n"
                       f"Datentyp: {column_data_type}\n")
                      # f"Werte: {column_values}")
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
            # distinct_values_of_current_col = get_column_distinct_column_values(table_name, col_name, db_id)
        metadata_mapping.append({
            "table": table_name,
            "column": col_name,
            "column_type": column_data_type,
          #  "column_value": column_values,

        })
        idx_col += 1

    db_embeddings = []
    for i in range(0, len(all_descriptions), batch_size):
        batch_descriptions = all_descriptions[i:i + batch_size]
        batch_embeddings = model.encode(
            batch_descriptions,
            convert_to_numpy=True,
            batch_size=batch_size,
            device="cpu", )
        db_embeddings.extend(batch_embeddings)

    dimension = len(db_embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(db_embeddings, dtype=np.float32))
    os.makedirs(embedd_fais_dict_path, exist_ok=True)
    faiss.write_index(index, os.path.join(embedd_fais_dict_path, "index.faiss"))

    with open(os.path.join(embedd_fais_dict_path, "metadata.json"), "w", encoding="utf-8") as f_meta:
        json.dump(metadata_mapping, f_meta, ensure_ascii=False, indent=2)"""

