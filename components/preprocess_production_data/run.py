# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Entry script for Model Data Collector Data Window Component."""

import argparse
import mltable
from spark.sql import SparkSession
import datetime


def mdc_preprocessor(
    data_window_start: str,
    data_window_end: str,
    input_data: str,
    preprocessed_input_data: str,
):
    start_datetime = datetime.strptime(data_window_start, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_datetime = datetime.strptime(data_window_end, "%Y-%m-%dT%H:%M:%S.%fZ")

    # table = mltable.from_parquet_files(paths=[{"folder": input_data}])

    # # In theory you should be able to filter on the date column, but the syntax is unclear to me.
    # # The line below somehow filter every event and the filter is not working.
    # filterStr = f"date >= datetime({start_datetime.year}, {start_datetime.month}, {start_datetime.day}, {start_datetime.hour}) and PartitionDate <= datetime({end_datetime.year}, {end_datetime.month}, {end_datetime.day}, {end_datetime.hour})"  # noqa
    # table = table.filter(filterStr)

    # # Lazy way to just use Pandas, not recommended in spark for large dataset
    # df = table.to_pandas_dataframe() # pandas dataframe
    # df["date"] = df["date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"))
    # df[(df["date"] >= start_datetime) & (df["date"] <= end_datetime)].sort_values("date")

    spark = SparkSession.builder.appName("AccessParquetFiles").getOrCreate()

    df = spark.read.parquet(input_data)  # spark dataframe
    df = df.withColumn("date", df["date"].cast("timestamp"))
    df = df.filter((df["date"] >= start_datetime) & (df["date"] <= end_datetime))
    df.write.parquet(preprocessed_input_data)

    df.to_parquet(preprocessed_input_data)
    table = mltable.from_parquet_files(paths=[{"file": preprocessed_input_data}])
    table.save(preprocessed_input_data)


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
