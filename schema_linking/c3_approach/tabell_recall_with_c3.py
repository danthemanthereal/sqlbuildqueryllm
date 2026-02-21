import json

def get_all_table_with_cols():

    schema_str = ""
    schema_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        databases = json.load(f)



    for db in databases:
        table_names = db["table_names"]
        column_names = db["column_names"]

        for table_idx, table in enumerate(table_names):
            schema_str = schema_str + " " + table + " ( "
            for col_idx, col in column_names:
                if col_idx == table_idx:
                    schema_str = schema_str + " " + col + ", "
            schema_str = schema_str + ")"

    return schema_str