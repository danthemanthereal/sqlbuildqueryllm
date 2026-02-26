import json
import time
import re
from data_preprocessing.german_spider_preprocessor import get_english_table_name
from structural_linking.gnn_spider_german_or_knowledge_graph import get_all_tables
import math
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
for idx, map in enumerate(new_table_col_map):
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
        continue

with open(f"{folder_path}/table_map_with_desc.json", "w", encoding="utf-8") as f:
    json.dump(table_map_with_desc, f, ensure_ascii=False, indent=4)
"""from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


model = SentenceTransformer('intfloat/multilingual-e5-small')
anchors = get_all_tables()
anchor_embeddings = model.encode(anchors)


new_ticket = ["Finden Sie den Namen des Mitarbeiters, der bei der Bewertung am häufigsten ausgezeichnet wurde."]
ticket_embedding = model.encode(new_ticket)


similarity_features = cosine_similarity(ticket_embedding, anchor_embeddings)

scores = similarity_features[0]

# Indizes der Top 5
top5_idx = np.argsort(scores)[-5:][::-1]

# passende Anchors + Scores
top5 = [(anchors[i], scores[i]) for i in top5_idx]
winner = []
for anchor, score in top5:
    winner.append(anchor)
    print(anchor, score)

eng = [ get_english_table_name(w) for w in winner]
print(eng)"""

"""except RateLimitError as e:
        try:
            logger.info(f"Die exception rate limit message {e.message}")
            error_message = str(e)

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
            logger.warning(f"Rate Limit Exceeded: bei Groq nach {retry_after} Sekunden noch mal probieren. Bei Firma {company_name}")
            time.sleep(retry_after)
            prompt = get_detailed_company_information_search_prompt(company_city_name, company_name, lat, lon)
            response = get_response(GROQ_COMPOUND_MINI_MODEL, prompt)

            logger.info(f"Ergebnis von Groq nach RateLimit für {company_name}  {company_city_name} mit folgender " +
                    f"Antwort: {response}")
            return json.loads(response)"""