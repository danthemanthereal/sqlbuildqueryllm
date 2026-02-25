import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import os

def create_embeddings(descriptions, batch_size=16):
    multi_lang_version = "intfloat/multilingual-e5-small"
    model = SentenceTransformer(multi_lang_version)

    db_embeddings = []
    for i in range(0, len(descriptions), batch_size):
        batch_descriptions = descriptions[i:i + batch_size]
        batch_embeddings = model.encode(
            batch_descriptions,
            convert_to_numpy=True,
            batch_size=batch_size,
            device="cpu", )
        db_embeddings.extend(batch_embeddings)

    dimension = len(db_embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(db_embeddings, dtype=np.float32))
    embedd_fais_dict_path="/Users/danielschmidt/Desktop/sqlbuildqueryllm/schema_linking/custom_chess_agentframe_work/faiss_total_db_index"
    faiss.write_index(index, os.path.join(embedd_fais_dict_path, "index.faiss"))


def get_results_to_a_question(question: str, top_k: int = 10):
    index = faiss.read_index("/Users/danielschmidt/Desktop/sqlbuildqueryllm/schema_linking/custom_chess_agentframe_work/faiss_total_db_index/index.faiss")
    multi_lang_version = "intfloat/multilingual-e5-small"
    model = SentenceTransformer(multi_lang_version)
    query_vector = model.encode(question)
    query_vector = query_vector.reshape(1, -1)
    distances, indices = index.search(query_vector, top_k)
    return indices[0].tolist()