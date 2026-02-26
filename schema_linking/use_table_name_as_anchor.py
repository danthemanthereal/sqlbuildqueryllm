from structural_linking.gnn_spider_german_or_knowledge_graph import get_all_tables
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from adjustText import adjust_text
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def get_most_similar_table_with_anchor(word: str):
    tables = get_all_tables()

    multi_lang_version = "intfloat/multilingual-e5-small"
    model = SentenceTransformer(multi_lang_version)

    table_embeddings = model.encode(tables)

    """pca = PCA(n_components=2)
    reduced = pca.fit_transform(embeddings)

    plt.figure(figsize=(8, 6))

    # nur Punkte
    plt.scatter(reduced[:, 0], reduced[:, 1])

    plt.title("PCA Projection of Table Embeddings")
    plt.xlabel("PC1")
    plt.ylabel("PC2")

    plt.show()

    k = 25  # Anzahl Cluster (frei wählbar)

    kmeans = KMeans(n_clusters=k, random_state=42)
    clusters = kmeans.fit_predict(embeddings)

    pca = PCA(n_components=2)
    reduced = pca.fit_transform(embeddings)

    plt.figure(figsize=(16, 12))

    plt.scatter(
        reduced[:, 0],
        reduced[:, 1],
        c=clusters  # Farbe = Cluster
    )

    plt.title("K-Means Clustering of Table Embeddings")
    plt.xlabel("PC1")
    plt.ylabel("PC2")

    plt.show()"""

    word_embeddings = model.encode([word])


    # Calculate similarity features
    similarity_features = cosine_similarity(word_embeddings, table_embeddings)

    similarity_features = cosine_similarity(
        word_embeddings,
        table_embeddings
    )

    # Array flach machen
    similarities = similarity_features[0]

    # Top 5 Indizes finden (höchste Ähnlichkeit)
    top_k = 5
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    #print("Top 5 ähnlichste Ergebnisse:\n")
    predicted_tables = []
    for rank, idx in enumerate(top_indices, 1):
       # print(f"{rank}. Tabelle: {tables[idx]}")
        #print(f"   Similarity: {similarities[idx]:.4f}\n")
        predicted_tables.append(tables[idx])
    return predicted_tables