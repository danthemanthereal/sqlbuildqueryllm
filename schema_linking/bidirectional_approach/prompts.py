def get_table_retrieval_prompt(SCHEMA, AUGMENTED_QUESTION, HINT):
    return f"""
You are tasked with identifying the relevant tables and all their columns from a database schema needed to write an SQL query from a natural language question. The schema is provided as a dictionary where keys are table names and values are lists of column names. You will receive:
- The original question
- A list of subquestions breaking down the original question into simpler parts - A list of keywords and keyphrases extracted from the question
- The schema containing tables and their full column lists
- An optional hint (if provided)
Your goal is to select the tables required to construct an SQL query that answers the question and include all columns from those tables. To ensure high recall, include any table that might be relevant based on the original question, subquestions, keywords, or hint, even if its relevance is uncertain.
Output the result as a JSON-formatted dictionary where keys are the selected table names and values are their full column lists, like {"table1": ["col1"], "table2": ["col2"]}.
Here are some examples: Example 1: [EXAMPLE] Example 2: [EXAMPLE] Example 3: [EXAMPLE]
Now, identify the relevant columns for the following: Schema: {SCHEMA}
Question Information: {AUGMENTED_QUESTION} Hint: {HINT}
Please respond with a JSON object structured as follows:
{
"chain of thought reasoning": "Your reasoning for selecting the columns, be concise and clear.",
"table name1": ["column1", "column2", ...],
"table name2": ["column1", "column2", ...],
...
}
Make sure your response includes the table names as keys, each associated with a list of column names that are necessary for writing a SQL query to answer the original question. Be cautious about the foreign keys.
For each aspect of the question, provide a clear and concise explanation of your reasoning behind selecting the columns. Do not include ““json in your response. Only output a json as your response.


"""

def get_coloumn_retrieval_prompt(SCHEMA, AUGMENTED_QUESTION, HINT):

    return f"""
You are tasked with identifying the relevant columns from a database schema needed to write an SQL query form a natural language question. The schema is provided as a dictionary where keys are table names and values are lists of column names (e.g., {"Employees": ["ID", "Name"]}). You will receive:
- The original question
- A list of subquestions breaking down the original question into simpler parts - A list of keywords and keyphrases extracted from the question
- The schema containing tables and their full column lists
- An optional hint (if provided)
Your goal is to select the columns from each table required to construct an SQL query that answers the question. To ensure high recall, include any column that might be relevant based on the original question, subquestions, or keywords, such as columns for filtering, joining, or computing results.
Output the result as a JSON-formatted dictionary where keys are the table names from the filtered schema and values are the selected column names, like {"table1": ["col1"], "table2": ["col2"]}.
Here are some examples: Example 1: [EXAMPLE] Example 2: [EXAMPLE] Example 3: [EXAMPLE]
Now, identify the relevant columns for the following: Schema: {SCHEMA}
Question Information: {AUGMENTED_QUESTION} Hint: {HINT}
Please respond with a JSON object structured as follows:
{
"chain of thought reasoning": "Your reasoning for selecting the columns, be concise and clear.",
"table name1": ["column1", "column2", ...],
"table name2": ["column1", "column2", ...],
...
}
Make sure your response includes the table names as keys, each associated with a list of column names that are necessary for writing a SQL query to answer the question. Be cautious about the foreign keys.
For each aspect of the question, provide a clear and concise explanation of your reasoning behind selecting the columns. Do not include ““json in your response. Only output a json as your response.
"""

def get_extract_key_words_prompt(SCHEMA, AUGMENTED_QUESTION, HINT, QUESTION, EVIDENCE):
    return f"""
Objective: Analyze the given question and hint to identify and extract keywords, keyphrases, and named entities. These elements are crucial for understanding the core components of the inquiry and the guidance provided. The goal is to recognize and isolate significant terms and phrases that could be instrumental in formulating searches or queries related to the posed question.
Instructions:
1. Read the Question Carefully: Identify the main focus, named entities (e.g., organizations,
locations), technical terms, and key concepts.
2. Analyze the Hint: Extract keywords or phrases that provide clarity or direction toward answering the question.
3. List Keyphrases and Entities: Combine findings from both the question and hint into a single Python list. Include:
• Keywords: Essential single words.
• Keyphrases: Multi-word terms or named entities.
Ensure all terms maintain the original phrasing or terminology used in the input.
Task:
Given the following question and hint, identify and list all relevant keywords, keyphrases, and named entities.
Question: {QUESTION} Hint: {EVIDENCE}
Please provide your findings as a json file, capturing the essence of both the question and hint through the identified terms and phrases.
   {
   "keywords": list of keywords, keyphrases and entities.
}
Do not include “‘json in your response. Only output a json object as your response.

"""