from data_preprocessing.stat_bot_swiss_preprocessing import table_meta_df
from vector_database.vector_db_for_table_describtion_swit_bot_dataset import collection

only_table_name = list(table_meta_df["name"])
table_description_df = table_meta_df[["name", "discription"]]

for table_name in only_table_name:
    results = collection.query(
        query_texts=table_name,
        n_results=3
    )
    print("Query:", table_name)
    print("Result:", results['documents'])
    description = table_description_df.loc[table_description_df["name"] == table_name, "discription"].values[0]
    print("richtiges ergebnis ",description )