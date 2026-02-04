from sentence_transformers import SentenceTransformer, util

from structural_linking.gnn_spider_german_or_knowledge_graph import get_all_tables, G

model = SentenceTransformer('all-MiniLM-L6-v2')

tables = get_all_tables(G)
sentences = [
    "Ich liebe Pizza",
    "Pizza macht mich glücklich",
    "Ich gehe heute spazieren"
]


embeddings = model.encode(tables)

threshold = 0.8


for i in range(len(tables)):
    for j in range(i + 1, len(tables)):
        similarity = util.cos_sim(embeddings[i], embeddings[j]).item()
        if similarity >= threshold:
            print(f"Sätze:\n  1: {tables[i]}\n  2: {tables[j]}")
            print(f"Ähnlichkeit: {similarity:.3f}\n")