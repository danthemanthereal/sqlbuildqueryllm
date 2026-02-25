from schema_linking.custom_auto_link.fill_schema import get_tables_with_tools
from schema_linking.custom_auto_link.retrieval_of_faiss_db import get_top_k_columns
import os

from schema_linking.custom_chess_agentframe_work.pipeline import get_relevant_tables

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

get_relevant_tables("Nenn mir alle Geschäfte in Berlin?")