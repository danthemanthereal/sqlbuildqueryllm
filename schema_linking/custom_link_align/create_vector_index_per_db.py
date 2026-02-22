import json
import os
from typing import Union, List
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import (
    SimpleDirectoryReader,
    Settings,
    SummaryIndex,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    PromptTemplate,
    get_response_synthesizer
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from sentence_transformers import SentenceTransformer

def build_index_per_db():
    schema_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/tables_de.json"

    with open(schema_path, "r", encoding="utf-8") as f:
        databases = json.load(f)

    for db in databases:
        # create per column a json file of the db
        #build_json_per_col_in_one_db(db)

        # build vector store  index per db
        build_vector_store_index_per_db(db)



def build_json_per_col_in_one_db(db):
    db_id = db["db_id"]
    tables = db["table_names"]
    columns = db["column_names"]
    column_info_lis = []
    colunm_per_json_dict_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/spider/json_files_per_col"


    for ind, (table_ind, col_name) in enumerate(columns):
        col_info = dict()
        col_info["column_name"] = col_name
        table_name = tables[table_ind]
        meta_data = {
            "db_id": db_id,
            "table_name": table_name
        }
        col_info["meta_data"] = meta_data
        column_info_lis.append(col_info)

    folder_path = rf"{colunm_per_json_dict_path}/{db_id}"
    os.makedirs(folder_path, exist_ok=True)

    for col in column_info_lis:
        table_name = col["meta_data"]["table_name"]
        col_name = col["column_name"]

        prefix = transform_name(table_name, col_name)
        print(f'file path {folder_path}/{prefix}.json')
        with open(rf'{folder_path}/{prefix}.json', 'w', encoding='utf-8') as f:
            json.dump(col, f, ensure_ascii=False, indent=4)


def transform_name(table_name, col_name):
    prefix = rf"{table_name}_{col_name}"
    prefix = prefix if len(prefix) < 100 else prefix[:100]

    syn_lis = ["(", ")", "%", "/"]
    for syn in syn_lis:
        if syn in prefix:
            prefix = prefix.replace(syn, "_")

    return prefix


def build_vector_store_index_per_db(db):
    db_id = db["db_id"]
    vector_idx_path = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/spider/database_vector_index"+"/"+db_id
    path_of_all_json_files_per_col = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/spider/json_files_per_col"
    schema_path = rf"{path_of_all_json_files_per_col}/{db_id}"
    build_index_from_source(
        data_source=schema_path,
        persist_dir=vector_idx_path + r"/vector_store",
        is_vector_store_exist=False,
        index_method="VectorStoreIndex"
    )

def build_index_from_source(
    data_source: Union[str, List[str]],
                persist_dir: str = None,
                is_vector_store_exist: bool = False,
                llm=None,
                index_method: str = None,
                embed_model_name=None,
                parser=None,
    ):
    # embedding model
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embed_model = HuggingFaceEmbedding(model_name)
    parser = SentenceSplitter(chunk_size=10000, chunk_overlap=0)

    index_method = None if index_method and index_method not in ["SummaryIndex",
                                                                 "VectorStoreIndex"] else index_method
    # parser of document



    # return if index already exists
    if is_vector_store_exist:
        if persist_dir is None:
            raise Exception("Pfad ist None von indexen ort")

        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)
        return index

    # save indices dict
    os.makedirs(persist_dir, exist_ok=True)

    is_dir = True

    if type(data_source) == List:
        is_dir = False
    elif type(data_source) == str:
        from pathlib import Path
        is_dir = Path(data_source).is_dir()

    is_vector_store_method = is_dir

    if index_method:
        is_vector_store_method = True if index_method == "VectorStoreIndex" else False

    if is_vector_store_method:

        documents = SimpleDirectoryReader(data_source).load_data()

        index = VectorStoreIndex.from_documents(
            documents, transformations=[parser],
            embed_model=embed_model,
            show_progress=True)


        index.storage_context.persist(persist_dir=persist_dir)
    else:
        if type(data_source) == List:
            documents = SimpleDirectoryReader(input_files=data_source).load_data()
        else:
            if not is_dir:
                documents = SimpleDirectoryReader(input_files=[data_source]).load_data()
            else:
                documents = SimpleDirectoryReader(data_source).load_data()

        index = SummaryIndex.from_documents(documents, transformations=[parser], show_progress=True)

        index.storage_context.persist(persist_dir=persist_dir)

    return index