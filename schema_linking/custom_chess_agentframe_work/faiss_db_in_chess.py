import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from structural_linking.gnn_spider_german_or_knowledge_graph import get_all_tables


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


# was not in the paper but embeddings of the table to a keyword -> in this dataset a lot of table
# means fast dass selbe -> get this also

def get_top_5_tables_based_on_key_word_meaning(keywords: list)->list:
    res = []

    for keyword in keywords:
        res.extend(get_best_table_based_on_keyword(keyword))
    return res

def get_best_table_based_on_keyword(keyword: str):
    multi_lang_version = "intfloat/multilingual-e5-small"
    model = SentenceTransformer(multi_lang_version)

    tables =get_all_tables()

    table_Key_word = tables + [keyword]

    tables_embeddings = model.encode(table_Key_word)

    keyword_embedding = tables_embeddings[-1].reshape(1, -1)

    table_embeddings_only = tables_embeddings[:-1]

    similarities = cosine_similarity(table_embeddings_only, keyword_embedding).flatten()

    top5_idx = similarities.argsort()[-5:][::-1]

    predicted_tables = [t for idx, t in enumerate(tables) if idx in top5_idx]
    return predicted_tables
