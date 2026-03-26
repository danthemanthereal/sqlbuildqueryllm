import json

def build_line_style_schema(table_list, column_list):
    schema_info = ["\n### Database\n-- Tables and Columns"]
    for table_name, column_item in zip(table_list, json.loads(column_list)):
        if column_item == "*":
            schema_info.append(f"{table_name}.{column_item}")
            continue
        for column_name, column_info in column_item.items():
            if column_name == "*":
                schema_info.append(f"{table_name}.{column_name}")
                continue
            column_data = {
                "type": column_info.get("type").upper(),
                "primary_key": bool(column_info.get("primary_key", False)),
            }
            if column_info.get("values"):
                value_list = []
                for v in column_info["values"]:
                    if type(v) is str and len(v) < 30:
                        value_list.append(v)
                    elif type(v) is int or type(v) is float:
                        value_list.append(v)
                if len(value_list) > 0:
                    column_data['values'] = value_list

            if column_info.get("description") and column_info["description"] != "" and len(
                    column_info["description"]) < 60:
                column_data['description'] = column_info["description"].strip()

            if column_info.get("comment") and column_info["comment"] != "" and len(column_info["comment"]) < 30:
                column_data['comment'] = column_info["comment"].strip()

            schema_info.append(f"{table_name}.{column_name} = {json.dumps(column_data)}")
    schema_info = "\n".join(schema_info)
    return schema_info


def merge_line_style_prompt(question, table_list, column_list, foreign_key, evidence):
    schema_text = build_line_style_schema(table_list, column_list)
    parts = [f"### Question\n{question.strip()}", schema_text]

    if foreign_key:
        fk_text = " | ".join(foreign_key)
        parts.append(f"\n-- Foreign Keys\n{fk_text}")

    if evidence:
        parts.append(f"\n-- Evidence\n{evidence.strip()}")

    return "\n".join(parts)

def handling_error(ques, table_list, column_list, foreign_key, evidence,error_msg, sql_pred):
    formatted_ques = merge_line_style_prompt(ques, table_list, column_list, foreign_key, evidence)

    # here mit messsages aufrufen ein model
    """prompt = format_chat(tokenizer, [
        {"role": "user", "content": formatted_ques},
        {"role": "assistant", "content": sql_pred},
        {"role": "user", "content": f"### Error Message\n{error_msg}"},
    ])"""

