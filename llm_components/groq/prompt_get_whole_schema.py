from schema_linking.c3_approach.tabell_recall_with_c3 import get_all_table_with_cols


def with_c3_prompt(question: str) -> str:

    instruction = """Given the database schema and question, perform the following actions: 
    1 - Rank all the tables based on the possibility of being used in the SQL according to the question from the most relevant to the least relevant, Table or its column that matches more with the question words is highly relevant and must be placed ahead.
    2 - Check whether you consider all the tables.
    3 - Output a list object in the order of step 2, Your output should contain all the tables. The format should be like: 
    [
        "table_1", "table_2", ...
    ]

    """
    schema = get_all_table_with_cols()
    prompt = instruction + "Schema:\n" + schema + "\n"
    prompt += "Question:\n" + question + "\n"

    return prompt