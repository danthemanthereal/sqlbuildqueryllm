from sentence_transformers import SentenceTransformer
from data_preprocessing.stat_bot_swiss_preprocessing import table_meta_df
import chromadb
client = chromadb.Client()

only_description_df = table_meta_df["discription"].dropna().astype(str).tolist()

table_description_df = table_meta_df[["name", "discription"]]

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

embeddings = model.encode(only_description_df)

collection = client.get_or_create_collection(name="table_description_stat_bot_data_set")
ids = [f"id{i}" for i in range(len(embeddings))]
collection.add(embeddings=embeddings,
               ids=ids,
               documents=only_description_df,
               metadatas=[{"name": n} for n in table_description_df["name"]])


