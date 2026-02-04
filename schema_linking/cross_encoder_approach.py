from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')  # kleines, schnelles Modell

# 2️⃣ Sätze, die wir vergleichen wollen
sentences = [
    "Ich liebe Pizza",
    "Pizza macht mich glücklich",
    "Ich gehe heute spazieren"
]

# 3️⃣ Sätze in Vektoren (Embeddings) umwandeln
embeddings = model.encode(sentences)

# 4️⃣ Ähnlichkeit berechnen (Cosine Similarity)
similarity_01 = util.cos_sim(embeddings[0], embeddings[1])  # Satz 0 vs Satz 1
similarity_02 = util.cos_sim(embeddings[0], embeddings[2])  # Satz 0 vs Satz 2

print(f"Ähnlichkeit zwischen Satz 0 und 1: {similarity_01.item():.3f}")
print(f"Ähnlichkeit zwischen Satz 0 und 2: {similarity_02.item():.3f}")