import json
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Optional
import networkx as nx



current_path = Path(__file__).resolve()
project_path = current_path.parent.parent
schema_path = project_path / "data" / "dataset_spider_de" / "multispider" / "with_english_value" / "tables_de.json"
schema_path_str = schema_path.as_posix()

class TableColumn:
    def __init__(self,
                 name: str,
                 text: str,
                 column_type: str,
                 is_primary_key: bool,
                 foreign_key: Optional[str]):
        self.name = name
        self.text = text
        self.column_type = column_type
        self.is_primary_key = is_primary_key
        self.foreign_key = foreign_key


class Table:
    def __init__(self,
                 name: str,
                 text: str,
                 columns: List[TableColumn]):
        self.name = name
        self.text = text
        self.columns = columns

def read_database_schema(schema_path: str) -> Dict[str, List[Table]]:
    schemas: Dict[str, Dict[str, Table]] = defaultdict(dict)
    dbs_json_blob = json.load(open(schema_path, "r"))
    for db in dbs_json_blob:
        db_id = db['db_id']

        column_id_to_table = {}
        column_id_to_column = {}

        for i, (column, text, column_type) in enumerate(
                zip(db['column_names_original'], db['column_names'], db['column_types'])):
            table_id, column_name = column
            _, column_text = text
            table_name = db['table_names_original'][table_id]

            if table_name not in schemas[db_id]:
                table_text = db['table_names'][table_id]
                schemas[db_id][table_name] = Table(table_name, table_text, [])

            if column_name == "*":
                continue

            is_primary_key = i in db['primary_keys']
            table_column = TableColumn(column_name.lower(), column_text, column_type, is_primary_key, None)
            schemas[db_id][table_name].columns.append(table_column)
            column_id_to_table[i] = table_name
            column_id_to_column[i] = table_column

        for (c1, c2) in db['foreign_keys']:
            foreign_key = column_id_to_table[c2] + ':' + column_id_to_column[c2].name
            column_id_to_column[c1].foreign_key = foreign_key

    return {**schemas}

schema = read_database_schema(schema_path_str)

# Knowledge graph


G = nx.MultiDiGraph()

for db_id, tables in schema.items():
    for table_name, table_obj in tables.items():

        table_node = f"table:{table_name}"
        G.add_node(table_node, type="table", db=db_id, name=table_name)

        for col in table_obj.columns:
            col_node = f"column:{table_name}.{col.name}"

            G.add_node(col_node,
                       type="column",
                       name=col.name,
                       table=table_name,
                       column_type=col.column_type)

            G.add_edge(table_node, col_node, relation="HAS_COLUMN")

            if col.is_primary_key:
                G.add_edge(table_node, col_node, relation="PRIMARY_KEY")

            if col.foreign_key:
                fk_table, fk_col = col.foreign_key.split(":")
                fk_node = f"column:{fk_table}.{fk_col}"
                G.add_edge(col_node, fk_node, relation="FOREIGN_KEY")



"""from pyvis.network import Network
print(f"Knoten: {G.number_of_nodes()}")
print(f"Kanten: {G.number_of_edges()}")
net = Network(notebook=True, height="750px", width="100%")
net.from_nx(G)
net.show("graph.html")"""