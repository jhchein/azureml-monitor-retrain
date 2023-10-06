import argparse
from pathlib import Path

import mlflow
import mltable
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dataset", type=str, required=True)

    parser.add_argument("--train_data", type=str, required=True)
    parser.add_argument("--test_data", type=str, required=True)
    parser.add_argument("--validation_data", type=str, required=True)

    parser.add_argument("--random_seed", type=int, default=None)

    args = parser.parse_args()

    return args


def main(args):
    tbl = mltable.load(args.input_dataset)
    data = tbl.to_pandas_dataframe()

    random_data = np.random.rand(len(data))

    msk_train = random_data < 0.7
    msk_val = (random_data >= 0.7) & (random_data < 0.85)
    msk_test = random_data >= 0.85

    train = data[msk_train]
    val = data[msk_val]
    test = data[msk_test]

    mlflow.log_metric("train size", train.shape[0])
    mlflow.log_metric("val size", val.shape[0])
    mlflow.log_metric("test size", test.shape[0])

    train.to_parquet((Path(args.train_data) / "train.parquet"))
    val.to_parquet((Path(args.validation_data) / "val.parquet"))
    test.to_parquet((Path(args.test_data) / "test.parquet"))


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
    ]

    for line in lines:
        print(line)

    main(args)

    mlflow.end_run()
