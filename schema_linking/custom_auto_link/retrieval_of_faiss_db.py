import faiss
import json
from sentence_transformers import SentenceTransformer
import os

def get_top_k_columns(question: str, top_k: int = 10):
    index_folder_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/schema_linking/custom_auto_link/embedded_documents"
    filtered_results = []
    model = SentenceTransformer('intfloat/multilingual-e5-small')
    for db in os.listdir(index_folder_path):
        index_file_path = index_folder_path + "/" + db + "/index.faiss"
        index = faiss.read_index(index_file_path)

        metadata_path = index_folder_path + "/" + db + "/metadata.json"
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata_mapping = json.load(f)


        question_embedding = model.encode(question)
        distances, indices = index.search(question_embedding.reshape(1, -1), len(metadata_mapping))


        for i in range(len(indices[0])):
            idx = int(indices[0][i])
            if 0 <= idx < len(metadata_mapping):
                metadata = metadata_mapping[idx]
                filtered_results.append({
                    "index": idx,
                    "distance": float(distances[0][i]),
                    "metadata": metadata
                })



    filtered_results.sort(key=lambda x: x["distance"])

    top_results = filtered_results[:top_k]

    return top_results