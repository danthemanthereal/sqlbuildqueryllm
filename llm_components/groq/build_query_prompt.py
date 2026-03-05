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
