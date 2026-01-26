import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer

PROJECT_PATH = Path(__file__).resolve().parents[1]

TABLE_METADATA_CSV_FILE_PATH = PROJECT_PATH.joinpath("data/StatBot_Swiss/meta_data_tables.csv")

table_meta_df = pd.read_csv(TABLE_METADATA_CSV_FILE_PATH)

only_german_table_df = table_meta_df[table_meta_df.lang == "de"]

only_description_df = table_meta_df["discription"].dropna().astype(str).tolist()

table_description_df = table_meta_df[["name", "discription"]]

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

embeddings = model.encode(only_description_df)

