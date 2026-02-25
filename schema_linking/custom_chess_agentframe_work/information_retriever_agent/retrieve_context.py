from typing import List


def find_predicted_tables(question: str, evidence: str, keywords: List[str], top_k: int):
    tables_with_descriptions = {}

    for keyword in keywords:
        question_based_query = f"{question} {keyword}"
        evidence_based_query = f"{evidence} {keyword}"

        retrieved_question_based_query = DatabaseManager().query_vector_db(question_based_query, top_k=top_k)
        retrieved_evidence_based_query = DatabaseManager().query_vector_db(evidence_based_query, top_k=top_k)

        tables_with_descriptions = self._add_description(tables_with_descriptions, retrieved_question_based_query)
        tables_with_descriptions = self._add_description(tables_with_descriptions, retrieved_evidence_based_query)

    return tables_with_descriptions