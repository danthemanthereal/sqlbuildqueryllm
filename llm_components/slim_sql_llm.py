from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

from structural_linking.gnn_spider_german_or_knowledge_graph import get_columns_of_table

model_name = "llmware/slim-sql-1b-v0"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32
)

def get_sql_query(tables, question):

    prompt = _get_prompt(tables)
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=False
        )

    sql = tokenizer.decode(output[0], skip_special_tokens=True)
    return sql

def _get_prompt(tables):
    pass

def _format_prompt(tables):
    schema_format_in_prompt = "Hier die Tabellen und Spalten die du nur berücksichtigen muss: \n"
    for table in tables:
        schema_format_in_prompt = schema_format_in_prompt + "Die Tabelle " + table + " \n folgenden Spalten: \n"
        schema_format_in_prompt += get_columns_of_table(table)





    return schema_format_in_prompt