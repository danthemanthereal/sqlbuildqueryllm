from sentence_transformers import SentenceTransformer, util

from structural_linking.gnn_spider_german_or_knowledge_graph import get_all_tables, G

model = SentenceTransformer('all-MiniLM-L6-v2')



def get_similarity_tables_and_sentence(sentence_tokens: list[str], question: str):
    tables = get_all_tables(G)
    token_embeddings = model.encode(sentence_tokens)
    table_embeddings = model.encode(tables)

    threshold = 0.8


    for i, token_emb in enumerate(token_embeddings):
        for j, table_emb in enumerate(table_embeddings):
            similarity = util.cos_sim(token_emb, table_emb).item()
            if similarity >= threshold:
                print("Frage:", question)
                print(f"Wort: {sentence_tokens[i]}")
                print(f"Tabelle: {tables[j]}")
                print(f"Ähnlichkeit: {similarity:.3f}\n")