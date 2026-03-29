from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re
import json
from question_decomposition.bidirectional_approach.prompts import get_question_decomposition_prompt
from schema_linking.bidirectional_approach.prompts import get_extract_key_words_prompt
from self_correction.agent_25_approach.prompts import DEFAULT_PROMPT_TEMPLATES
from sql_generation_comp.bidirectional_approach.prompt import get_generate_query_prompt
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
db_schema = None

def get_query_with_mistral(question: str, predicted_tables: list, correct_db_id) -> str:
    global db_schema
    db_schema = build_db_schema_based_on_predicted_tables(predicted_tables, correct_db_id)

    sub_question_prompt = get_question_decomposition_prompt(question)
    inputs_sub_question = tokenizer(sub_question_prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs_sub_question, max_new_tokens=300)
    generated_tokens = outputs[0][inputs_sub_question["input_ids"].shape[1]:]
    sub_questions = tokenizer.decode(generated_tokens, skip_special_tokens=True)

    key_words_prompt = get_extract_key_words_prompt(question, "")
    inputs_key_words = tokenizer(key_words_prompt, return_tensors="pt").to("cuda")
    key_words = model.generate(**inputs_key_words, max_new_tokens=300)
    key_words = tokenizer.decode(key_words[0][inputs_key_words["input_ids"].shape[1]:], skip_special_tokens=True)

    #prompt = get_generate_query_prompt(db_schema, question + sub_questions + key_words, "")
    #prompt = build_query_prompt(question, db_schema)
    #inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    prompt = get_generate_query_prompt(db_schema, question+ str(sub_questions) + str(key_words), "")
    messages = [
        {
            "role": "system",
            "content": "You are a strict SQL generator. "
                       "You maybe given several databases with several database id"
                       "You choose one of the database schema to use for building the query"
                       "Your criteria for using the database is to look on the tables and columns of the "
                       "database. Select the database where you think are the tables and columns to answer the question. "
                       "After selecting one database schema, you work only with the tables and columns of the selected databas schema."
                       "You only output valid SQL queries. No explanations."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        return_tensors="pt"
    ).to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=300)

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if "[/INST]" in result:
        result = result[result.index("[/INST]") + len("[/INST]"):]


    result.strip()
    try:
        data = json.loads(result)

        if isinstance(data, str):
            data = json.loads(data)

        if isinstance(data, dict):
            sql_query = data.get("SQL", "").strip()
            sql_query = sql_query.replace("\\", "")
        else:
            print("un else no dict ")
            sql_query = result
            sql_query = sql_query.replace("\\", "")
            sql_query = sql_query.replace('"SQL:"', "")
            sql_query = sql_query.replace("{", "")
            sql_query = sql_query.replace("}", "")
            print(f"in end dict {sql_query}")
    except json.JSONDecodeError:
        sql_query = result
    print("return squety", sql_query)
    print("type of sql_query", type(sql_query))
    if '"SQL"' in sql_query:
        print("in if because json string")
        sql_query = sql_query.replace("\\", "")
        sql_query_dict = json.loads(sql_query)
        sql_query = sql_query_dict["SQL"].strip()
        return sql_query.strip()
    return sql_query.strip()


def build_db_schema_based_on_predicted_tables(tables: list, correct_db_id) -> str:
    db_schema_sting = ""
    tables = list(dict.fromkeys(tables))
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
        if db_id != correct_db_id:
            continue
        db_schema_sting += f"Database : {db_id}\n"
        db_schema_sting += f"Tables and columns of the database:\n"
        all_tables = db_table_schema_map.get(db_id)
        for table in all_tables:

            col_of_table = get_columns_of_table_of_one_db(db_id, table)
            db_schema_sting += f"{table}({','.join(col_of_table)}) \n"
            relation_ships_of_the_table = get_relations_of_one_db(db_id,table)
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
                - Only use tables and columns from the schema
                - Output ONLY SQL
                - No explanation
                - Start with SELECT
                - End with semicolon

                SQL:
            """


def return_corrected_sql_wrapper(error_message, init_sql):
    return return_corrected_sql(db_schema, error_message, init_sql, "If the error is that no column exists, maybe try another table of a database schema.")
def return_corrected_sql(schema_context, error,initial_sql, hint):

    agent_25_approcha_prompt = DEFAULT_PROMPT_TEMPLATES.get("generic")
    filled_prompt = agent_25_approcha_prompt.format(schema_context=schema_context,
    nlq=error,
    initial_sql=initial_sql,
    hint=hint)
    messages = [
        {
            "role": "system",
            "content": "You are a an expert for correcting sql queries. You correct only the sql query based on the given database, the error and the false generated query. You only output valid SQL queries. No explanations."
        },
        {
            "role": "user",
            "content": filled_prompt,
        },

    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        return_tensors="pt"
    ).to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=100)

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if "[/INST]" in result:
        result = result[result.index("[/INST]") + + len("[/INST]"):]

    return result.strip()


def clean_sql(text):
    text = text.strip()

    match = re.search(r"```sql\s*(.*?)```", text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()

    return text