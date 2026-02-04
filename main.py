import json

from data_preprocessing.preprocessor import reprocess
from data_preprocessing.stat_bot_swiss_preprocessing import table_meta_df, only_german_test_df, query_question_test_df
from schema_linking.cross_encoder_approach import get_similarity_tables_and_sentence
from vector_database.vector_db_for_table_describtion_swit_bot_dataset import collection, embeddings, model
from transformers import AutoTokenizer
from torch import nn, cosine_similarity
from collections import Counter

"""only_table_name = list(table_meta_df["name"])
table_description_df = table_meta_df[["name", "discription"]]
only_question = list(only_german_test_df["question"])
query_end_question = query_question_test_df
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-german-cased")
embedding_dim = 768
table_embeddings = embeddings
table_in_query = 0
table_not_in_query = 0


for question in only_question:
    #pre_processed_words = reprocess(question)
    results = collection.query(
        query_texts=["".join([w.text for w in pre_processed_words]) + " datenbank tabelle beschreibung"],
        n_results=1
    )
    top_docs = results["documents"][0]
    top_scores = results["distances"][0]

    print("Query:", pre_processed_words)
    for doc, score in zip(top_docs, top_scores):
        print(score, doc)
    #tokens = tokenizer.tokenize(question)
    token_counts = Counter(tokens)
    input_ids = tokenizer(question, return_tensors="pt")["input_ids"]
    vocab = {token: idx for idx, token in enumerate(token_counts)}
    vocab_size = tokenizer.vocab_size
    word_embeddings = nn.Embedding(vocab_size, embedding_dim)(input_ids)
    bi_lstm = nn.LSTM(input_size=embedding_dim, hidden_size=128, bidirectional=True, batch_first=True)
    outputs, (hn, cn) = bi_lstm(word_embeddings)
    query_vector = outputs.mean(dim=1)
    #query_vector = model.encode(tokens, convert_to_tensor=True)
    #scores = cosine_similarity(query_vector, table_embeddings)
    #print("scores ")
    #print(scores)
    results = collection.query(
        query_texts=[question],
        n_results=8
    )

    query_wert = query_question_test_df.loc[query_question_test_df['question'] == question, 'query'].values[0]
    metadata_liste = results["metadatas"][0]

    ergebnis = any(item["name"] in query_wert for item in metadata_liste)
    if ergebnis is True:
        table_in_query += 1
    else:
        table_not_in_query += 1

print("table correct in query:", table_in_query)
print("table not in query:", table_not_in_query)


    #description = table_description_df.loc[table_description_df["name"] == table_name, "discription"].values[0]
    #print("richtiges ergebnis ",description )"""


json_file = "/Users/danielschmidt/Desktop/sqlbuildqueryllm/data/dataset_spider_de/multispider/with_original_value/dev_de.json"

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)
for i, entry in enumerate(data):

    question = "".join(entry.get("question"))
    if entry.get('question'):
        #print(f"type oif  {type(entry.get('question'))}")
        #print(f"question: {question}")
        get_similarity_tables_and_sentence(entry.get("question").split(" "), entry.get("question"))