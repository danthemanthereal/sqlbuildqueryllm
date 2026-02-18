import json
from collections import defaultdict


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