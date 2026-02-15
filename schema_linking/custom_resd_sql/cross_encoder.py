from collections import defaultdict

from transformers import BertTokenizer, BertForSequenceClassification
import torch
import json

tokenizer = BertTokenizer.from_pretrained("bert-base-german-cased")
model = BertForSequenceClassification.from_pretrained("bert-base-german-cased", num_labels=1)  # 1 Score


def get_formated_schema():
    schema_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        databases = json.load(f)

    db_strings = []

    for db in databases:
        table_names = db["table_names"]  # deutsche Namen
        column_names = db["column_names"]

        schema = defaultdict(list)

        for table_idx, column_name in column_names:
            if table_idx == -1:
                continue
            table_name = table_names[table_idx]
            schema[table_name].append(column_name)

        parts = []
        for table, columns in schema.items():
            parts.append(f"{table}: {', '.join(columns)}")

        schema_sequence = " | ".join(parts)

        db_strings.append(schema_sequence)

    return "\n".join(db_strings)

def get_relevant_tables_and_columns(question: str):
    schema = get_formated_schema()
    input_sequence = question + " | " + schema






