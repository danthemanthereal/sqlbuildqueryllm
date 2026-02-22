import json
import os


def build_index_per_db():
    schema_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"

    with open(schema_path, "r", encoding="utf-8") as f:
        databases = json.load(f)

    for db in databases:
        # create per column a json file of the db
        build_json_per_col_in_one_db(db)




        # create an index per db


def build_json_per_col_in_one_db(db):
    db_id = db["db_id"]
    tables = db["table_names"]
    columns = db["column_names"]
    column_info_lis = []
    colunm_per_json_dict_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/spider/json_files_per_col"


    for ind, (table_ind, col_name) in enumerate(columns):
        col_info = dict()
        col_info["column_name"] = col_name
        table_name = tables[table_ind]
        meta_data = {
            "db_id": db_id,
            "table_name": table_name
        }
        col_info["meta_data"] = meta_data
        column_info_lis.append(col_info)

    folder_path = rf"{colunm_per_json_dict_path}/{db_id}"
    os.makedirs(folder_path, exist_ok=True)

    for col in column_info_lis:
        table_name = col["meta_data"]["table_name"]
        col_name = col["column_name"]

        prefix = transform_name(table_name, col_name)
        print(f'file path {folder_path}/{prefix}.json')
        with open(rf'{folder_path}/{prefix}.json', 'w', encoding='utf-8') as f:
            json.dump(col, f, ensure_ascii=False, indent=4)


def transform_name(table_name, col_name):
    prefix = rf"{table_name}_{col_name}"
    prefix = prefix if len(prefix) < 100 else prefix[:100]

    syn_lis = ["(", ")", "%", "/"]
    for syn in syn_lis:
        if syn in prefix:
            prefix = prefix.replace(syn, "_")

    return prefix