import argparse
import os

import mlflow
import mltable
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser()
    # Inputs
    parser.add_argument("--input_dataset", type=str, required=True)

    # Outputs
    parser.add_argument("--train_data", type=str, required=True)
    parser.add_argument("--test_data", type=str, required=True)
    parser.add_argument("--validation_data", type=str, required=True)

    # Parameters
    parser.add_argument("--random_state", type=int, default=None, required=False)

    args = parser.parse_args()

    return args


def main(args):
    tbl = mltable.load(args.input_dataset)

    df = tbl.to_pandas_dataframe()
    df = df.drop(columns=["timestamp"])

    # Set random state (considered safer than np.random.seed())
    rng = np.random.default_rng(args.random_state)
    random_data = rng.random(len(df))

    msk_train = random_data < 0.7
    msk_val = (random_data >= 0.7) & (random_data < 0.85)
    msk_test = random_data >= 0.85

    train = df[msk_train]
    val = df[msk_val]
    test = df[msk_test]

    mlflow.log_metric("train size", train.shape[0])
    mlflow.log_metric("val size", val.shape[0])
    mlflow.log_metric("test size", test.shape[0])

    os.makedirs(args.train_data, exist_ok=True)
    os.makedirs(args.test_data, exist_ok=True)
    os.makedirs(args.validation_data, exist_ok=True)

    train.to_parquet(args.train_data + "/data.parquet", index=False)
    test.to_parquet(args.test_data + "/data.parquet", index=False)
    val.to_parquet(args.validation_data + "/data.parquet", index=False)


if __name__ == "__main__":
    mlflow.start_run()

    # ---------- Parse Arguments ----------- #
    # -------------------------------------- #

    args = parse_args()

    lines = [
        f"Raw data path: {args.input_dataset}",
        f"Train dataset output path: {args.train_data}",
        f"Val dataset output path: {args.validation_data}",
        f"Test dataset path: {args.test_data}",
        f"Random state: {args.random_state}",
    ]

    for line in lines:
        print(line)

    main(args)

    mlflow.end_run()
