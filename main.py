from schema_linking.custom_auto_link.fill_schema import get_tables_with_tools
from schema_linking.custom_auto_link.retrieval_of_faiss_db import get_top_k_columns
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

get_tables_with_tools("Wie viele SängerIn haben wir?")