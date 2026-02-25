# 3 Schritt
# Fokus auf

from typing import List

from schema_linking.custom_chess_agentframe_work.faiss_db_in_chess import get_results_to_a_question


def find_predicted_tables(question: str, evidence: str, keywords: List[str], top_k: int):
    tables_with_descriptions = {}

    for keyword in keywords:
        question_based_query = f"{question} {keyword}"
        evidence_based_query = f"{evidence} {keyword}"

        retrieved_question_based_query = get_results_to_a_question(question_based_query, top_k=10)
        retrieved_evidence_based_query = get_results_to_a_question(evidence_based_query, top_k=10)
        print(retrieved_question_based_query)
        print(retrieved_evidence_based_query)

       # tables_with_descriptions = self._add_description(tables_with_descriptions, retrieved_question_based_query)
        #tables_with_descriptions = self._add_description(tables_with_descriptions, retrieved_evidence_based_query)

    return tables_with_descriptions
