import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from structural_linking.gnn_spider_german_or_knowledge_graph import get_all_tables, get_columns_of_table, G


def get_relevant_columns(db_schema_graph, question: str):
    model_name = "mistralai/Mistral-7B-Instruct-v0.2"

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        use_fast=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        output_hidden_states=True
    )

    text = _build_prompt_for_decoder_model(db_schema_graph, question)

    inputs = tokenizer(
        text,
        return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        outputs = model(**inputs)

    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    print("tokens:", tokens)
    for i, tok in enumerate(tokens):
        print(i, tok)


def _build_prompt_for_decoder_model(db_schema_graph, question: str):
    prompt = f"Die Frage: {question} \n"

    tables = get_all_tables(db_schema_graph)

    for table in tables:
        columns_of_table = get_columns_of_table(db_schema_graph, table)
        prompt += _format_for_prompt(table, columns_of_table)

    return prompt

def _format_for_prompt(table: str, columns):
    return f"{table} \n  " + "\n - ".join(columns) + "\n"

get_relevant_columns(G, "")

