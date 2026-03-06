from structural_linking.gnn_spider_german_or_knowledge_graph import get_columns_of_table, get_relations_per_db
from google import genai


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



def generate_query_by_gemma(question: str, predicted_tables: list) -> str:
    client = genai.Client(api_key="AIzaSyBfGCHKxGfTaqdhpPoGTJaQZFXTSZZ2uj4")

    db_schema = build_db_schema_based_on_predicted_tables(predicted_tables)
    prompt = build_query_prompt(question, db_schema)
    response = client.models.generate_content(
        model="gemma-3-27b-it",
        contents=prompt,
    )


    return response.text



def build_db_schema_based_on_predicted_tables(tables: list) ->str:
    db_schema_sting = ""

    for table in tables:
        col_of_table = get_columns_of_table(table)
        relation_ships_of_the_table = get_relations_per_db(table)

        db_schema_sting += f"table: {table} with columns: {col_of_table} \n"
        db_schema_sting += f" relation ship with other tables: {relation_ships_of_the_table}\n"



    return db_schema_sting