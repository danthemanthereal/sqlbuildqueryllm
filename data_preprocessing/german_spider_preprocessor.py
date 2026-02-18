import json


def get_german_english_translation_map():
    json_file = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"
    german_english_table_mapping = {}

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    for i, entry in enumerate(data):
        german_tables = entry["table_names"]
        english_tables = entry["table_names_original"]

        for de, en in zip(german_tables, english_tables):
            german_english_table_mapping[de] = en

    return german_english_table_mapping

def get_english_table_name(german_table_name: str):
    mapping = get_german_english_translation_map()
    return mapping.get(german_table_name, "")