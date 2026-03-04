import json


def get_all_splitted_german_spider():
    json_file = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/dev_de.json"
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    def chunk_list(lst, chunk_size):
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

    chunked_data = chunk_list(data, 250)