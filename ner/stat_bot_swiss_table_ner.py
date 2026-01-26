import pandas as pd
from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parents[1]

TABLE_METADATA_CSV_FILE_PATH = PROJECT_PATH.joinpath("data/StatBot_Swiss/meta_data_tables.csv")

table_meta_df = pd.read_csv(TABLE_METADATA_CSV_FILE_PATH)

only_german_table_df = table_meta_df[table_meta_df.lang == "de"]

#print(only_german_table_df[["name", "discription"]])
