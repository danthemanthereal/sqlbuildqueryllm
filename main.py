from schema_linking.custom_auto_link.fill_schema import get_tables_with_tools
from schema_linking.custom_auto_link.vector_db_faiss import embed_documents
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
embed_documents(16)