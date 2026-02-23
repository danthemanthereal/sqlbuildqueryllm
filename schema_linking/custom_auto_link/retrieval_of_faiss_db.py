import faiss
import json
from sentence_transformers import SentenceTransformer


def get_top_k_columns(question: str, db_id: str, top_k: int = 5):
    index_folder_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/schema_linking/custom_auto_link/embedded_documents"
    index_file_path = index_folder_path + "/" + db_id + "/index.faiss"
    index = faiss.read_index(index_file_path)

    metadata_path = index_folder_path + "/" + db_id + "/metadata.json"
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata_mapping = json.load(f)

    model = SentenceTransformer('intfloat/e5-small-v2')
    question_embedding = model.encode(question)
    distances, indices = index.search(question_embedding.reshape(1, -1), len(metadata_mapping))
    filtered_results = []

    for i in range(len(indices[0])):
        idx = int(indices[0][i])
        if 0 <= idx < len(metadata_mapping):
            metadata = metadata_mapping[idx]
            filtered_results.append({
                "index": idx,
                "distance": float(distances[0][i]),
                "metadata": metadata
            })
            if len(filtered_results) >= top_k:
                break

    return filtered_results, len(metadata_mapping)

