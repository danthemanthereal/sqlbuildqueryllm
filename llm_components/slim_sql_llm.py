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
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=False
        )

    sql = tokenizer.decode(output[0], skip_special_tokens=True)
    return sql

def _get_prompt(tables, question):
    return f"""
        Du bist ein Experte in Generieren von SQL Queries zu einer Frage. 
        Du gehst so vor, dass du zu dieser Frage {question} eine SQL Query erstellst. 
        
        Dabei darfst du nur folende Tabellen, Spalten und Fremdbeziehungen zwischen den Tabellen benutzen:
         {_format_prompt(tables)}
         
       Dabei gehst du Schritt für Schritt vor und kontrollierst dich in jedem Zwischenschritt, ob 
       du nur Tabellen und Spalten und Fremdbeziehungen benutzt hast die du gegeben bekommen hast.
       Außerdem prüfst du auch in jedem Zwischenschritt ob die Frage {question} auch auf die gebaute Query passt.   

        Deine Antwort erhält nur die generierte Query ohne extra Kommentar oder so.
    """

def _format_prompt(tables):
    schema_format_in_prompt = "Hier die Tabellen und Spalten die du nur berücksichtigen muss: \n"
    for table in tables:
        schema_format_in_prompt = schema_format_in_prompt + "Die Tabelle " + table + " \n folgenden Spalten: \n"
        schema_format_in_prompt += get_columns_of_table(table)
        schema_format_in_prompt = schema_format_in_prompt + "\n Mit den Folgenden Frembbeziehungen zu anderen Tabellen: \n  "
        schema_format_in_prompt = schema_format_in_prompt + get_foreign_keys_of_table(table)
        schema_format_in_prompt = schema_format_in_prompt + "\n "

    return schema_format_in_prompt




    return schema_format_in_prompt