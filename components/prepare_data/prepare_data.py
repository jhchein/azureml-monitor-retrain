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


def store_mltable(df, dest_path):
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    # Datastore URI azureml://subscriptions/13c1109b-ba76-4ca6-8161-8767bdf3c75c/resourcegroups/ai-services-rg/workspaces/schaeffler-ops-it-aml/datastores/workspaceblobstore/paths/azureml/105b677d-845f-44c6-b0be-caedcec0a5b1/train_data/
    # Relative path azureml/105b677d-845f-44c6-b0be-caedcec0a5b1/train_data/
    # Ideal path azureml://datastores/<credential_datastore_name>/paths/<path_to_data>
    # How do I get the datastore name? Just use default?

    azureml_short_path = (
        f"azureml://datastores/workspaceblobstore/paths/{dest_path}/data.parquet"
    )

    df.to_parquet(dest_path + "/data.parquet", index=False)
    tbl = mltable.from_parquet_files(paths=[{"file": azureml_short_path}])
    tbl.save(dest_path, overwrite=False)


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

    store_mltable(train, args.train_data)
    store_mltable(val, args.validation_data)
    store_mltable(test, args.test_data)


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
