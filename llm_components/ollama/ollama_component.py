from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

from structural_linking.gnn_spider_german_or_knowledge_graph import get_columns_of_table, get_relations_per_db, \
    get_db_id_and_tables, get_columns_of_table_of_one_db, get_relations_of_one_db

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

print("Lade Modell einmal...")

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16
).to("cuda")

print("Modell geladen!")


def get_query_with_mistral(question: str, predicted_tables: list) -> str:
    db_schema = build_db_schema_based_on_predicted_tables(predicted_tables)
    prompt = build_query_prompt(question, db_schema)
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    messages = [
        {
            "role": "system",
            "content": "You are a strict SQL generator. You only output valid SQL queries. No explanations."
        },
        {
            "role": "user",
            "content": f"""
    Generate a SQL query for the following question.

    SCHEMA:
    {db_schema}

    QUESTION:
    {question}

    RULES:
    - Only use tables and columns from the schema
    - Output ONLY SQL
    - No explanation
    - Start with SELECT
    - End with semicolon
    """
        }
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        return_tensors="pt"
    ).to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=100)

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if "[/INST]" in result:
        result = result[result.index("[/INST]")++ len("[/INST]"):]


    return result.strip()


def build_db_schema_based_on_predicted_tables(tables: list) -> str:
    db_schema_sting = ""
    tables = list(dict.fromkeys(tables))
    print("tables: ", tables)
    print("----")
    tables_per_db_id = get_db_id_and_tables()
    db_table_schema_map = {}

    for table in tables:
        for key, current_table in tables_per_db_id.items():
            if table in current_table:
                if key in db_table_schema_map:
                    if table not in db_table_schema_map[key]:
                        db_table_schema_map[key].append(table)
                else:
                    db_table_schema_map[key] = [table]
    for db_id, tables in db_table_schema_map.items():
        db_schema_sting += f"Database : {db_id}\n"
        db_schema_sting += f"Tables and columns of the database:\n"
        all_tables = db_table_schema_map.get(db_id)
        for table in all_tables:

            col_of_table = get_columns_of_table_of_one_db(db_id, table)

            db_schema_sting += f"table: {table} with columns: {col_of_table} \n"
            relation_ships_of_the_table = get_relations_of_one_db(db_id,table)
            db_schema_sting += f" relation ship with other tables: {relation_ships_of_the_table}\n"

    print("db schema string")
    print(db_schema_sting)
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
                - Only use tables and columns from the schema
                - Output ONLY SQL
                - No explanation
                - Start with SELECT
                - End with semicolon

                SQL:
            """
