def build_query_prompt(question, schema):
    return f"""
        Act like an expert for generating SQL queries for a question. 
        
        ***** TASK***
        You are given a question and a database schema. 
        Your task is to generate a SQL query for a question based only use 
        information like table column and joins only based on the givin database schema.
        
        Question: {question}
        
        Database schema: {schema}
"""