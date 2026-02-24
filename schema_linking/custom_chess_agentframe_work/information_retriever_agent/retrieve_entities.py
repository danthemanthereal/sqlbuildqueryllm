# Schritt 2
# Dieser Code definiert eine Klasse RetrieveEntity,
# die aus einer Frage und einem Hinweis (Hint)
# automatisch relevante Spalten und Werte einer Datenbank identifiziert.
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer
import difflib
import numpy as np

from schema_linking.custom_chess_agentframe_work.db_schema_ln_this_approach import get_db_schema_dict


def get_similar_columns(question: str, key_words: list) -> list:
    pass


def find_columns_by_name():
    pass


def find_columns_by_semantic(question: str, keywords: list, hint: str):
    potential_column_names = []
    for keyword in keywords:
        keyword = keyword.strip()
        potential_column_names.append(keyword)

        column, value = column_value(keyword)
        if column:
            potential_column_names.append(column)

        potential_column_names.extend(extract_paranthesis(keyword))

        if " " in keyword:
            potential_column_names.extend(part.strip() for part in keyword.split())

    schema = get_db_schema_dict()
    to_embed_strings = []

    column_strings = [f"`{table}`.`{column}`" for table, columns in schema.items() for column in columns]
    question_hint_string = f"{question} {hint}"

    to_embed_strings.extend(column_strings)
    to_embed_strings.append(question_hint_string)

    model = SentenceTransformer("intfloat/e5-small-v2")

    column_strings = [
            f"passage: `{table}`.`{column}`"
            for table, columns in schema.items()
            for column in columns
        ]

    question_hint_string = f"query: {question} {hint}"

    to_embed_strings = column_strings + [question_hint_string]

    embeddings = model.encode(
            to_embed_strings,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

    column_embeddings = embeddings[:-1]
    question_hint_embedding = embeddings[-1]

    similar_column_names = []

    for i, column_embedding in enumerate(column_embeddings):
            table, column = column_strings[i].split('.')[0].strip('`'), column_strings[i].split('.')[1].strip('`')
            for potential_column_name in potential_column_names:
                if _does_keyword_match_column(potential_column_name, column):
                    similarity_score = np.dot(column_embedding, question_hint_embedding)
                    similar_column_names.append((table, column, similarity_score))

    similar_column_names.sort(key=lambda x: x[2], reverse=True)
    table_column_pairs = list(set([(table, column) for table, column, _ in similar_column_names]))
    return table_column_pairs


def column_value(string: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Splits a string into column and value parts if it contains '='.

    Args:
        string (str): The string to split.

    Returns:
        Tuple[Optional[str], Optional[str]]: The column and value parts.
    """
    if "=" in string:
        left_equal = string.find("=")
        first_part = string[:left_equal].strip()
        second_part = string[left_equal + 1:].strip() if len(string) > left_equal + 1 else None
        return first_part, second_part
    return None, None


def extract_paranthesis(string: str) -> List[str]:
    """
        Extracts strings within parentheses from a given string.

        Args:
            string (str): The string to extract from.

        Returns:
            List[str]: A list of strings within parentheses.
    """
    matches = []
    stack = []

    for i, char in enumerate(string):
        if char == "(":
            stack.append(i)
        elif char == ")" and stack:
            start = stack.pop()
            matches.append(string[start + 1:i])  # ohne ()

    return matches


def _does_keyword_match_column(self, keyword: str, column_name: str, threshold: float = 0.9) -> bool:
    """
    Checks if a keyword matches a column name based on similarity.

    Args:
        keyword (str): The keyword to match.
        column_name (str): The column name to match against.
        threshold (float, optional): The similarity threshold. Defaults to 0.9.

    Returns:
        bool: True if the keyword matches the column name, False otherwise.
    """
    keyword = keyword.lower().replace(" ", "").replace("_", "").rstrip("s")
    column_name = column_name.lower().replace(" ", "").replace("_", "").rstrip("s")
    similarity = difflib.SequenceMatcher(None, column_name, keyword).ratio()
    return similarity >= threshold
