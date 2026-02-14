import json
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Optional
import networkx as nx

from data_preprocessing.german_spider_preprocessor import get_english_table_name

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
            _, column_text = column
            table_name = db['table_names_original'][table_id]

            if table_name not in schemas[db_id]:
                table_text = db['table_names_original'][table_id]
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


def read_database_schema_german(schema_path: str) -> Dict[str, List[Table]]:
    schemas: Dict[str, Dict[str, Table]] = defaultdict(dict)
    dbs_json_blob = json.load(open(schema_path, "r"))
    for db in dbs_json_blob:
        db_id = db['db_id']

        column_id_to_table = {}
        column_id_to_column = {}

        for i, (column, text, column_type) in enumerate(
                zip(db['column_names_original'], db['column_names'], db['column_types'])):
            table_id, column_name = text
            _, column_text = text
            table_name = db['table_names'][table_id]

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

# Knowledge graph

def get_graph():
    G = nx.MultiDiGraph()
    current_path = Path(__file__).resolve()
    project_path = current_path.parent.parent
    schema_path = project_path / "data" / "dataset_spider_de" / "multispider" / "with_english_value" / "tables_de.json"
    schema_path_str = schema_path.as_posix()
    schema = read_database_schema(schema_path_str)
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
    return G


def get_graph_german():
    G = nx.MultiDiGraph()
    current_path = Path(__file__).resolve()
    project_path = current_path.parent.parent
    schema_path = project_path / "data" / "dataset_spider_de" / "multispider" / "with_english_value" / "tables_de.json"
    schema_path_str = schema_path.as_posix()
    schema = read_database_schema_german(schema_path_str)
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
    return G

def get_all_tables():
    G = get_graph_german()
    tables = [data["name"] for node, data in G.nodes(data=True) if data.get("type") == "table"]
    return tables

def get_all_columns():
    G = get_graph()
    columns = [data["name"] for node, data in G.nodes(data=True) if data.get("type") == "column"]
    return columns


def get_columns_of_table(table_name):
    G = get_graph()
    table_node = f"table:{table_name}"

    if table_node not in G:
        return []
    columns = [
        G.nodes[neighbor]["name"]
        for neighbor in G.successors(table_node)
        if G.nodes[neighbor].get("type") == "column"
    ]

    return columns


def get_foreign_keys_of_table(table_name):
    G = get_graph()
    table_node = f"table:{table_name}"
    fks = []

    if table_node not in G:
        return []

    for neighbor in G.successors(table_node):
        if G.nodes[neighbor].get("type") != "column":
            continue

        for _, target, edge_data in G.out_edges(neighbor, data=True):
            if edge_data.get("relation") == "FOREIGN_KEY":
                fks.append({
                    "column": G.nodes[neighbor]["name"],
                    "references": target.replace("column:", "")
                })

    return fks

def get_db_id_and_tables():
    map_db_id_table_in_correct_order= {}
    current_path = Path(__file__).resolve()
    project_path = current_path.parent.parent
    schema_path = project_path / "data" / "dataset_spider_de" / "multispider" / "with_english_value" / "tables_de.json"
    schema_path_str = schema_path.as_posix()

    with open(schema_path_str, "r", encoding="utf-8") as f:
        schema = json.load(f)

    for element in schema:
        map_db_id_table_in_correct_order[element.get("db_id")] = element.get("table_names_original")
    return map_db_id_table_in_correct_order


def get_gold_tables_of_db(db_id, valid_index_list):
    db_table_map = get_db_id_and_tables()
    all_tables = db_table_map.get(db_id, [])
    filtered_tables = [table for idx, table in enumerate(all_tables) if idx in valid_index_list]
    return filtered_tables


"""from pyvis.network import Network
print(f"Knoten: {G.number_of_nodes()}")
print(f"Kanten: {G.number_of_edges()}")
net = Network(notebook=True, height="750px", width="100%")
net.from_nx(G)
net.show("graph.html")"""