# 3 Schritt
# Fokus auf

from typing import List

from schema_linking.custom_chess_agentframe_work.db_schema_ln_this_approach import get_db_schema_descriptions
from schema_linking.custom_chess_agentframe_work.faiss_db_in_chess import get_results_to_a_question


def find_predicted_tables(question: str, evidence: str, keywords: List[str], top_k: int):
    tables_with_descriptions = {}
    predicted_tables = []
    all_descriptions = get_db_schema_descriptions()
    for keyword in keywords:
        question_based_query = f"{question} {keyword}"
        evidence_based_query = f"{evidence} {keyword}"

        retrieved_question_based_query = get_results_to_a_question(question_based_query, top_k=10)
        retrieved_evidence_based_query = get_results_to_a_question(evidence_based_query, top_k=10)
        for retrieved_idx in retrieved_question_based_query:
            predicted_tables.append(all_descriptions[retrieved_idx])
        for retrieved_idx in retrieved_evidence_based_query:
            predicted_tables.append(all_descriptions[retrieved_idx])


       # tables_with_descriptions = self._add_description(tables_with_descriptions, retrieved_question_based_query)
        #tables_with_descriptions = self._add_description(tables_with_descriptions, retrieved_evidence_based_query)

    return predicted_tables
