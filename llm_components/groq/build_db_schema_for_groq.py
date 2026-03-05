from structural_linking.gnn_spider_german_or_knowledge_graph import get_columns_of_table, get_relations_per_db


def build_db_schema_based_on_predicted_tables(tables: list) ->str:
    db_schema_sting = ""

    for table in tables:
        col_of_table = get_columns_of_table(table)
        relation_ships_of_the_table = get_relations_per_db(table)

        db_schema_sting += f"table: {table} with columns: {col_of_table} \n"
        db_schema_sting += f" relation ship with other tables: {relation_ships_of_the_table}\n"



    return db_schema_sting