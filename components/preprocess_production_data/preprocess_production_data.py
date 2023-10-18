import argparse
import mlflow
import mltable
import pandas as pd
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_data", type=str, required=True)
    parser.add_argument(
        "--data_window_start",
        type=str,
        required=True,
        help="Example: 2023-05-01T04:31:57.012Z",
    )
    parser.add_argument(
        "--data_window_end",
        type=str,
        required=True,
        help="Example: 2023-05-01T04:31:57.012Z",
    )
    parser.add_argument("--preprocessed_data", type=str, required=True)

    args = parser.parse_args()

    return args


def main(args):
    input_parquet_path = Path(args.input_data) / "data.parquet"

    df = pd.read_parquet(input_parquet_path)

    df["date"] = pd.to_datetime(df["date"])
    df = df[
        (df["date"] >= args.data_window_start) & (df["date"] <= args.data_window_end)
    ]

    output_parquet_path = Path(args.preprocessed_data) / "preprocessed_data.parquet"
    df.to_parquet(output_parquet_path)
    tbl = mltable.from_parquet_files(paths=[{"file": output_parquet_path}])
    tbl.save(args.preprocessed_data)


if __name__ == "__main__":
    mlflow.start_run()

    # ---------- Parse Arguments ----------- #
    # -------------------------------------- #

    args = parse_args()

    lines = [
        f"Raw data path: {args.input_data}",
        f"Preprocessed data output path: {args.preprocessed_data}",
        f"Data window start: {args.data_window_start}",
        f"Data window end: {args.data_window_end}",
    ]

    for line in lines:
        print(line)

    main(args)

    mlflow.end_run()
