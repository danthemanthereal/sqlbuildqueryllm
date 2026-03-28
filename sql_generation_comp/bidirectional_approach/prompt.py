def get_generate_query_prompt(SCHEMA, AUGMENTED_QUESTION, EVIDENCE):
    return f"""
    You are a data science expert. Below, you are presented with a database schema and a question. Your task is to read the schema, understand the question, and generate a valid SQLite query to answer the original question.
Before generating the final SQL query, think step by step about how to write the query.
Database Schema: {SCHEMA}
This schema offers an in-depth description of the database’s architecture, detailing tables, columns, primary keys, foreign keys, and any pertinent information regarding relationships or constraints. Special attention should be given to the examples listed beside each column (if any), as they directly hint at which columns are relevant to our query.
Database admin instructions:
- Only output the information explicitly asked in the question. If the question asks for a specific column, include only that column in the SELECT clause.
- The predicted query should return all of the information asked in the question—nothing more, nothing less.
Question Information: {AUGMENTED_QUESTION} Hint: {EVIDENCE}
The question information, including subquestions and keywords, is designed to guide your focus toward the most relevant parts of the schema needed to answer the question effectively.
Please respond with a JSON object structured as follows:
   {{ "SQL": "Your SQL query in a single string." }}
Priority should be given to columns that have been explicitly matched with examples relevant to the question’s context.
Take a deep breath and think step by step to find the correct SQLite SQL query for the original question.
    """