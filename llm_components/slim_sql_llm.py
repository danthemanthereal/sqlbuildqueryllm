from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

from structural_linking.gnn_spider_german_or_knowledge_graph import get_columns_of_table, get_foreign_keys_of_table


model_name = "llmware/slim-sql-1b-v0"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32
    )

def get_sql_query(tables, question):

    prompt = _get_prompt(tables,question)
    print(f"prompt {prompt}")
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=False
        )

    prompt_len = inputs["input_ids"].shape[1]
    generated_tokens = output[0][prompt_len:]

    sql = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()"""
    return ""

def _get_prompt(tables, question):
    return f"""
You are an expert text-to-SQL system.

Given the database schema below, write a single valid SQLite SQL query
that answers the given question.

QUESTION (may be in German):
{question}

DATABASE SCHEMA:
{_format_prompt(tables)}

RULES:
- Use only the tables and columns listed above.
- Use correct JOIN conditions based on foreign keys.
- Return ONLY the SQL query.
- Do NOT include explanations or comments.
- The output must start with SELECT.

SQL:
"""


def _format_prompt(tables):
    schema = ""
    for table in tables:
        schema += f"Table {table}:\n"
        schema += "  Columns: " + ", ".join(get_columns_of_table(table)) + "\n"

        fks = get_foreign_keys_of_table(table)
        if fks:
            schema += "  Foreign Keys:\n"
            for fk in fks:
                schema += f"    {fk['column']} -> {fk['references']}\n"
        schema += "\n"
    return schema
