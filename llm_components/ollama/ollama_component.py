from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re
import json
from question_decomposition.bidirectional_approach.prompts import get_question_decomposition_prompt
from schema_linking.bidirectional_approach.prompts import get_extract_key_words_prompt
from self_correction.agent_25_approach.prompts import DEFAULT_PROMPT_TEMPLATES
from sql_generation_comp.bidirectional_approach.prompt import get_generate_query_prompt
from sql_generation_comp.chess_sql_gen_apporach.prompt import first_prompt_of_chess
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




def get_query_with_mistral(question: str, predicted_tables: list, db_id) -> str:
    global db_schema
    db_schema = build_db_schema_based_on_predicted_tables(predicted_tables, db_id)

    #sub_question_prompt = get_question_decomposition_prompt(question)
    #inputs_sub_question = tokenizer(sub_question_prompt, return_tensors="pt").to("cuda")
    #outputs = model.generate(**inputs_sub_question, max_new_tokens=300)
    #generated_tokens = outputs[0][inputs_sub_question["input_ids"].shape[1]:]
    #sub_questions = tokenizer.decode(generated_tokens, skip_special_tokens=True)

    #key_words_prompt = get_extract_key_words_prompt(question, "")
    #inputs_key_words = tokenizer(key_words_prompt, return_tensors="pt").to("cuda")
    #key_words = model.generate(**inputs_key_words, max_new_tokens=300)
    #key_words = tokenizer.decode(key_words[0][inputs_key_words["input_ids"].shape[1]:], skip_special_tokens=True)

    #prompt = get_generate_query_prompt(db_schema, question + sub_questions + key_words, "")
    #prompt = build_query_prompt(question, db_schema)
    #inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    prompt = get_prompt_with_question_decom_and_table_link(db_schema, question)
    messages = [
        {
            "role": "system",
            "content": "You are a an expert for generation a correct sql query for a question."
                       "You maybe given several databases with several database id"
                       "You choose one of the database schema to use for building the query"
                       "Your criteria for using the database is to look on the tables and columns of the "
                       "database. Select the database where you think are the tables and columns to answer the best the question. "
                       "After selecting one database schema, you work only with the tables and columns of the selected database schema."
                       "You only output one valid SQL query. No explanations."
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
    sql_query = sql_query.replace("\\", "")
    print("return squety", sql_query)
    print("type of sql_query", type(sql_query))

    return sql_query.strip()


def build_db_schema_based_on_predicted_tables(tables: list, db_id_par: str) -> str:
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
        if db_id != db_id_par:
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
    return return_corrected_sql( db_schema, error_message, init_sql, "If the error is that no column exists, maybe try another table of a database schema.")
def return_corrected_sql(schema_context, error,initial_sql, hint):
    print(f"schema in correction {schema_context}")
    agent_25_approcha_prompt = DEFAULT_PROMPT_TEMPLATES.get("generic")
    filled_prompt = agent_25_approcha_prompt.format(schema_context=schema_context,
    nlq=error,
    initial_sql=initial_sql,
    hint=hint)
    messages = [
        {
            "role": "system",
            "content":
                "You are a an expert for correcting sql queries. "
                "You correct only the sql query based on the given database, the error and the false generated query. "
                "You only output one valid SQL query. No explanations."
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
    outputs = model.generate(**inputs, max_new_tokens=300)

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


def get_question_decomp_prompt(question, db_schema)->str:
    return f"""    
### SQLite SQL tables, with their properties:
# document_types (document_type_code, document_description)
# documents (document_id, document_type_code, grant_id, sent_date, response_-
received_date, other_details)
# grants (grant_id, organisation_id, grant_amount, grant_start_date, grant_end_date,
other_details)
# organisation_types (organisation_type, organisation_type_description)
# organisations (organisation_id, organisation_type, organisation_details)
# project_outcomes (project_id, outcome_code, outcome_details)
# project_staff (staff_id, project_id, role_code, date_from, date_to, other_details)
# projects (project_id, organisation_id, project_details)
# research_outcomes (outcome_code, outcome_description)
# research_staff (staff_id, employer_organisation_id, staff_details)
# staff_roles (role_code, role_description)
# tasks (task_id, project_id, task_details, eg agree objectives)
#
### Question:  Find out the send dates of the documents with the grant amount of
more than 5000 were granted by organisation type described as "Research".
decompose the question
1.  Find out the send dates of the documents.
2.  Find out the send dates of the documents with the grant amount of more than
5000.
3.  Find out the send dates of the documents with the grant amount of more than 5000
were granted by organisation type described as "Research".
# Thus, the answer for the question is:  Find out the send dates of the documents
with the grant amount of more than 5000 were granted by organisation type described
as "Research".
SELECT T1.sent_date FROM documents AS T1 JOIN Grants AS T2 ON T1.grant_id =
T2.grant_id JOIN Organisations AS T3 ON T2.organisation_id = T3.organisation_id
JOIN organisation_Types AS T4 ON T3.organisation_type = T4.organisation_type WHERE
T2.grant_amount > 5000 AND T4.organisation_type_description = ’Research’
### SQLite SQL tables, with their properties:
# stadium (stadium_id, location, name, capacity, highest, lowest, average)
# singer (singer_id, name, country, song_name, song_release_year, age, is_male)
# concert (concert_id, concert_name, theme, stadium_id, year)
# singer_in_concert (concert_id, singer_id)
#
### Question:  {question}
### Database schema:{db_schema}
decompose the question and use with the given Database schema the question. 
Return only a sql query without any comments or explanation.  
"""

def get_prompt_with_question_decom_and_table_link(question, database_schema):
    return f"""
### SQLite SQL tables, with their properties:
# document_types (document_type_code, document_description)
# documents (document_id, document_type_code, grant_id, sent_date, response_-
received_date, other_details)
# grants (grant_id, organisation_id, grant_amount, grant_start_date, grant_end_date,
other_details)
# organisation_types (organisation_type, organisation_type_description)
# organisations (organisation_id, organisation_type, organisation_details)
# project_outcomes (project_id, outcome_code, outcome_details)
# project_staff (staff_id, project_id, role_code, date_from, date_to, other_details)
# projects (project_id, organisation_id, project_details)
# research_outcomes (outcome_code, outcome_description)
# research_staff (staff_id, employer_organisation_id, staff_details)
# staff_roles (role_code, role_description)
# tasks (task_id, project_id, task_details, eg agree objectives)
#
### Question:  Find out the send dates of the documents with the grant amount of
more than 5000 were granted by organisation type described as "Research".
decompose the question
1.  Find out the send dates of the documents.
SQL table (column):  documents (sent_date)
2.  Find out the send dates of the documents with the grant amount of more than
5000.
SQL table (column):  grants (grant_amount, grant_id)
3.  Find out the send dates of the documents with the grant amount of more than 5000
were granted by organisation type described as "Research".
SQL table (column):  organisation_Types (organisation_type_description,
organisation_type), organisations (organisation_type, organisation_id)
# Thus, the answer for the question is:  Find out the send dates of the documents
with the grant amount of more than 5000 were granted by organisation type described
as "Research".
SELECT T1.sent_date FROM documents AS T1 JOIN Grants AS T2 ON T1.grant_id =
T2.grant_id JOIN Organisations AS T3 ON T2.organisation_id = T3.organisation_id
JOIN organisation_Types AS T4 ON T3.organisation_type = T4.organisation_type WHERE
T2.grant_amount > 5000 AND T4.organisation_type_description = ’Research’
### SQLite SQL tables, with their properties:
{database_schema}
#
### Question:  {question}
decompose the question and use only the given Tables and columns. 
Return only a sql query without any comments or explanation.  
"""