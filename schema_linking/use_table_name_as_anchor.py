from structural_linking.gnn_spider_german_or_knowledge_graph import get_all_tables
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from adjustText import adjust_text

def get_most_similar_table_with_anchor(word: str):
    tables = get_all_tables()

    multi_lang_version = "intfloat/multilingual-e5-small"
    model = SentenceTransformer(multi_lang_version)

    embeddings = model.encode(tables)

    """pca = PCA(n_components=2)
    reduced = pca.fit_transform(embeddings)

    plt.figure(figsize=(8, 6))

    # nur Punkte
    plt.scatter(reduced[:, 0], reduced[:, 1])

    plt.title("PCA Projection of Table Embeddings")
    plt.xlabel("PC1")
    plt.ylabel("PC2")

    plt.show()"""