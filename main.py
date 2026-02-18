from schema_linking.custom_e_sql.get_table_based_value_in_col import get_table_column_map, go_all_dbs, \
    get_table_column_map_per_db_id

table_col_per_db_id = get_table_column_map_per_db_id()

print(table_col_per_db_id)