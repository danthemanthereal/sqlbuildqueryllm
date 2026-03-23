from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

from structural_linking.gnn_spider_german_or_knowledge_graph import get_columns_of_table, get_relations_per_db


def get_query_with_mistral(question: str, predicted_tables: list)->str:
    model_name = "mistralai/Mistral-7B-Instruct-v0.2"

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16
    ).to("cuda")

    db_schema = build_db_schema_based_on_predicted_tables(predicted_tables)
    prompt = build_query_prompt(question, db_schema)
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    outputs = model.generate(**inputs, max_new_tokens=100)

    return tokenizer.decode(outputs[0])


def build_db_schema_based_on_predicted_tables(tables: list) ->str:
    db_schema_sting = ""

    for table in tables:
        col_of_table = get_columns_of_table(table)
        relation_ships_of_the_table = get_relations_per_db(table)

        db_schema_sting += f"table: {table} with columns: {col_of_table} \n"
        db_schema_sting += f" relation ship with other tables: {relation_ships_of_the_table}\n"



    return db_schema_sting

def build_query_prompt(question, schema):
    return f"""
                You are an expert SQL generator.

                TASK:
                Generate a SQL query that answers the question using ONLY the given schema.

                SCHEMA:
                {schema}

                QUESTION:
                {question}

                RULES:
                - Use only tables and columns from the schema.
                - Do NOT explain anything.
                - Do NOT output reasoning.
                - Do NOT output markdown.
                - Output ONLY the SQL query.
                - The first word of your response must be SELECT.

                SQL:
            """