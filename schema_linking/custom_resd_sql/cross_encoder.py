from collections import defaultdict
from sentence_transformers import CrossEncoder
from sentence_transformers import SentenceTransformer
from transformers import BertTokenizer, BertForSequenceClassification, BertModel
import torch
import json

tokenizer = BertTokenizer.from_pretrained("bert-base-german-cased")
model = BertModel.from_pretrained("bert-base-german-cased")
cross_encoder_model_name = "cross-encoder/ms-marco-MiniLM-L-12-v2"
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")

def get_formated_schema():
    schema_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        databases = json.load(f)

    db_strings = []

    for db in databases:
        table_names = db["table_names"]
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

       # schema_sequence = " | ".join(parts)

            db_strings.append(f"{table}: {', '.join(columns)}")

    return db_strings

def get_relevant_tables_and_columns(question: str):
    schema = get_formated_schema()
    # form like in the paper
    schema_elements = get_formated_schema()
    cross_encoder_input = [question] + schema_elements

    # customized schema input
    schema_question_pairs = [(question, table_column) for table_column in schema_elements]

    # cross encoder
    scores = cross_encoder.predict(schema_question_pairs)
    tok_k =3
    topk = sorted(
        zip(schema_elements, scores),
        key=lambda x: x[1],
        reverse=True
    )[:tok_k]



    # get top k table und top k columns

    top_tables_k = 3
    top_columns_k = 5

    tables = [
        element.split(":", 1)[0].strip()
        for element in schema_elements
    ]

    table_pairs = [(question, t) for t in tables]
    table_scores = cross_encoder.predict(table_pairs)

    table_ranking = sorted(
        zip(tables, table_scores),
        key=lambda x: x[1],
        reverse=True
    )

    top_tables = table_ranking[:top_tables_k]


















