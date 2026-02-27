from structural_linking.gnn_spider_german_or_knowledge_graph import get_all_tables
import math
import json
import time
import re
import os

def safe_json_loads(text):
    import re, json

    text = text.strip()

    # markdown entfernen
    text = text.replace("```json", "").replace("```", "")

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON detected:\n{text}")

    return json.loads(match.group())


folder_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value"
from groq import Groq, RateLimitError

table_json_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"

with open(table_json_path, "r", encoding="utf-8") as f:
    db_schema = json.load(f)

new_table_col_map = []
for db in db_schema:
    tables = db["table_names"]
    col_names = db["column_names"]
    db_id = db["db_id"]
    for idx, t in enumerate(tables):
        current_cols = []
        for table_id, col in col_names:
            if table_id == idx:
                current_cols.append(col)
        new = {
            "table_name": t,
            "column_names": current_cols,
            "db_id": db_id,
            "table_description": [],
            "column_description": [],
            "fks": [],
            "pks": []
        }
        new_table_col_map.append(new)

api_key = "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"
table_map_with_desc = []
llm = Groq(api_key=api_key)
output_file = f"{folder_path}/table_map_with_desc.json"

if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as f:
        table_map_with_desc = json.load(f)
else:
    table_map_with_desc = []
for idx, map in enumerate(new_table_col_map[258:],start=258):
    try:
        if idx % 5 == 0:
            time.sleep(5)
        db_id = map["db_id"]
        fks = map["fks"]
        pks = map["pks"]
        table_name = map["table_name"]
        column_names = map["column_names"]
        table_desc = ""
        column_descs = []
        user_prompt = f"Tabelle: {map['table_name']} Spalten: {map['column_names']}"
        system_prompt = """
        Du bist ein Experte für Tabellenbeschreibungen für RAG-Systeme.

        Du bekommst:
        - einen Tabellennamen
        - eine Liste von Spalten

        Gib EXAKT EIN gültiges JSON-Objekt zurück im Format:

        {
          "table_description": "kurze präzise Beschreibung der Tabelle",
          "column_descriptions": [
            "Beschreibung Spalte 1",
            "Beschreibung Spalte 2"
          ]
        }

        Rules:
        Descriptions only in german.
        Return ONLY valid JSON.
        Do not use markdown.
        Do not wrap in ```json.
        """
        res = llm.chat.completions.create(
            model="groq/compound",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        ).choices[0].message.content
        data = safe_json_loads(res)
        table_desc = data["table_description"]
        column_descs = data["column_descriptions"]
        print({
            "table_name": table_name,
            "table_description": table_desc,
            "column_names": column_names,
            "column_descriptions": column_descs,
            "db_id": db_id,
            "fks": fks,
            "pks": pks
        })
        table_map_with_desc.append({
            "table_name": table_name,
            "table_description": table_desc,
            "column_names": column_names,
            "column_descriptions": column_descs,
            "db_id": db_id,
            "fks": fks,
            "pks": pks
        })
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(table_map_with_desc, f, ensure_ascii=False, indent=4)
        print(f"idx {idx}")
    except RateLimitError as e:
        error_message = str(e)
        print(error_message)
        match = re.search(
            r"try again in\s*(?:(\d+)m)?\s*(?:(\d+(?:\.\d+)?)s)?",
            error_message,
        )

        retry_after = 60
        if match:
            minutes = int(match.group(1)) if match.group(1) else 0
            seconds = float(match.group(2)) if match.group(2) else 0.0

            retry_after = math.ceil(minutes * 60 + seconds)

        retry_after += 1
        print("retry after ", retry_after)
        time.sleep(retry_after)
        res = llm.chat.completions.create(
            model="groq/compound",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        ).choices[0].message.content
        data = safe_json_loads(res)
        table_desc = data["table_description"]
        column_descs = data["column_descriptions"]
        print("after retry ")
        print({
            "table_name": table_name,
            "table_description": table_desc,
            "column_names": column_names,
            "column_descriptions": column_descs,
            "db_id": db_id,
            "fks": fks,
            "pks": pks
        })
        table_map_with_desc.append({
            "table_name": table_name,
            "table_description": table_desc,
            "column_names": column_names,
            "column_descriptions": column_descs,
            "db_id": db_id,
            "fks": fks,
            "pks": pks
        })
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(table_map_with_desc, f, ensure_ascii=False, indent=4)
        print(f"idx {idx}")
    except Exception as e:
        print("in execption")
        print(e)
        print({
            "table_name": table_name,
            "table_description": table_desc,
            "column_names": column_names,
            "column_descriptions": column_descs,
            "db_id": db_id,
            "fks": fks,
            "pks": pks
        })
        table_map_with_desc.append({
            "table_name": table_name,
            "table_description": table_desc,
            "column_names": column_names,
            "column_descriptions": column_descs,
            "db_id": db_id,
            "fks": fks,
            "pks": pks
        })
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(table_map_with_desc, f, ensure_ascii=False, indent=4)
        continue
        print(f"idx {idx}")

