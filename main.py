from schema_linking.custom_auto_link.fill_schema import get_tables_with_tools
from schema_linking.custom_auto_link.retrieval_of_faiss_db import get_top_k_columns
import os
from schema_linking.custom_chess_agentframe_work.db_schema_ln_this_approach import get_db_schema_descriptions
from schema_linking.custom_chess_agentframe_work.faiss_db_in_chess import create_embeddings
from schema_linking.custom_chess_agentframe_work.pipeline import get_relevant_tables

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

predictedt_tables = get_relevant_tables("Was sind die besten Gebäude?")
print(predictedt_tables)