from typing import List

from pandas import DataFrame
from sentence_transformers import SentenceTransformer
from data_preprocessing.stat_bot_swiss_preprocessing import table_meta_df
import chromadb
client = chromadb.Client()

def _get_embeddings_text(data_frame: DataFrame) -> List[str]:
    embeddings_texts = []
    for _, row in data_frame.iterrows():
        text = f"{row['name']}: {row['discription']}"
        embeddings_texts.append(text)
    return embeddings_texts

only_description_df = table_meta_df["discription"].dropna().astype(str).tolist()

table_description_df = table_meta_df[["name", "discription"]]

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

documents_list = table_description_df["discription"].tolist()

embedding_texts = _get_embeddings_text(table_description_df)
embeddings = model.encode(embedding_texts, convert_to_tensor=True)

collection = client.get_or_create_collection(name="table_description_stat_bot_data_set")
ids = [f"id{i}" for i in range(len(embeddings))]
collection.add(embeddings=embeddings.tolist(),
               ids=ids,
               documents=embedding_texts,
               metadatas=[{"name": n} for n in table_description_df["name"]])

