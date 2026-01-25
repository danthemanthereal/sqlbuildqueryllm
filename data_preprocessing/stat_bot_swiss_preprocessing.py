import pandas as pd
from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parents[1]

TEST_CSV_FILE_PATH = PROJECT_PATH.joinpath("data/StatBot_Swiss/test.csv")

TRAIN_CSV_FILE_PATH = PROJECT_PATH.joinpath("data/StatBot_Swiss/train.csv")

test_df = pd.read_csv(TEST_CSV_FILE_PATH)
train_df = pd.read_csv(TRAIN_CSV_FILE_PATH)

only_german_test_df = test_df[test_df.lang == 'de']
only_german_train_df = train_df[train_df.lang == 'de']

query_question_test_df = only_german_test_df[['query', 'question']]
query_question_train_df = only_german_train_df[['query', 'question']]