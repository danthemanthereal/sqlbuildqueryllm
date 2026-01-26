import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_PATH = Path(__file__).resolve().parents[1]

TABLE_METADATA_CSV_FILE_PATH = PROJECT_PATH.joinpath("data/StatBot_Swiss/meta_data_tables.csv")

table_meta_df = pd.read_csv(TABLE_METADATA_CSV_FILE_PATH)
print(table_meta_df.columns.tolist())
only_german_table_df = table_meta_df[table_meta_df.lang == "de"]

#print(only_german_table_df[["name", "discription"]])
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

texts = [
"Berlin",
"Stadt in Deutschland",
"italienisch",
"Art der Küche"
]


# Embeddings berechnen
embeddings = model.encode(texts)


# Ähnlichkeit berechnen
similarity_matrix = cosine_similarity(embeddings)


print(similarity_matrix)