# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Entry script for Custom Production Data Preprocessing Component."""

import argparse
import os
import tempfile
from datetime import datetime

from azureml.fsspec import AzureMachineLearningFileSystem
from dateutil import parser
from pyspark.sql import SparkSession


def init_spark():
    """Get or create spark session."""
    spark = SparkSession.builder.appName("AccessParquetFiles").getOrCreate()
    return spark


def save_spark_df_as_mltable(metrics_df, folder_path: str):
    """Save spark dataframe as mltable."""
    metrics_df.write.option("output_format", "parquet").option(
        "overwrite", True
    ).mltable(folder_path)


def mdc_preprocessor(
    data_window_start: str,
    data_window_end: str,
    input_data: str,
    preprocessed_input_data: str,
):
    format_data = "%Y-%m-%d %H:%M:%S"
    start_datetime = parser.parse(data_window_start)
    start_datetime = datetime.strptime(
        str(start_datetime.strftime(format_data)), format_data
    )

    end_datetime = parser.parse(data_window_end)
    end_datetime = datetime.strptime(
        str(end_datetime.strftime(format_data)), format_data
    )

    print(f"Start datetime: {start_datetime}")
    print(f"End datetime: {end_datetime}")

    spark = init_spark()
    df = spark.read.parquet(input_data)

    print(f"Total lines: {df.count()}")

    df = df.withColumn("timestamp", df["timestamp"].cast("timestamp"))
    df = df.filter(
        (df["timestamp"] >= start_datetime) & (df["timestamp"] <= end_datetime)
    )

    print(f"Total lines after filtering: {df.count()}")

    if df.count() == 0:
        raise Exception(
            "The window for this current run contains no data. "
            + "Please visit aka.ms/mlmonitoringhelp for more information."
        )

    # Create MLTable in different location
    save_path = tempfile.mktemp()
    os.makedirs(save_path)
    df.write.parquet(os.path.join(save_path, "production.parquet"))

    des_path = preprocessed_input_data + "temp"
    fs = AzureMachineLearningFileSystem(des_path)
    fs.upload(
        lpath=save_path,  # local path
        rpath="",  # remote path
        **{"overwrite": "MERGE_WITH_OVERWRITE"},
        recursive=True,
    )

    save_spark_df_as_mltable(df, preprocessed_input_data)


def run():
    """Compute data window and preprocess data from MDC."""
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_window_start", type=str)
    parser.add_argument("--data_window_end", type=str)
    parser.add_argument("--input_data", type=str)
    parser.add_argument("--preprocessed_input_data", type=str)
    args = parser.parse_args()

    mdc_preprocessor(
        args.data_window_start,
        args.data_window_end,
        args.input_data,
        args.preprocessed_input_data,
    )


if __name__ == "__main__":
    run()
