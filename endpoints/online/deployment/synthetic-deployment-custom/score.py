import json
import logging
import os

import mlflow
import pandas as pd
from azureml.ai.monitoring import Collector
from mlflow.pyfunc.scoring_server import infer_and_parse_json_input

# from io import StringIO
# , predictions_to_json


def init():
    global model
    global input_schema
    global inputs_collector, outputs_collector, inputs_outputs_collector

    inputs_collector = Collector(
        name="model_inputs", on_error=lambda e: logging.info("ex:{}".format(e))
    )
    outputs_collector = Collector(
        name="model_outputs", on_error=lambda e: logging.info("ex:{}".format(e))
    )
    inputs_outputs_collector = Collector(
        name="model_inputs_outputs", on_error=lambda e: logging.info("ex:{}".format(e))
    )

    # "model" is the path of the mlflow artifacts when the model was registered. For automl
    # models, this is generally "mlflow-model".
    model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "model")
    print("model_path:{}".format(model_path))
    print("model_path_content:{}".format(os.listdir(model_path)))
    model = mlflow.pyfunc.load_model(model_path)
    input_schema = model.metadata.get_input_schema()


def preprocess(json_data):
    if "input_data" not in json_data.keys():
        raise Exception("Request must contain a top level key named 'input_data'")

    # preprocess the payload to ensure it can be converted to pandas DataFrame
    serving_input = json.dumps(json_data["input_data"])
    data = infer_and_parse_json_input(serving_input, input_schema)
    return data


def run(raw_data):
    # raw json: {"input_data":
    #   {"columns": ['Pregnancies','PlasmaGlucose','DiastolicBloodPressure','TricepsThickness','SerumInsulin','BMI','DiabetesPedigree','Age'],
    #   "data": [[1.0, 78.0, 41.0, 33.0, 311.0, 50.79639151, 0.420803683, 24.0],[0.0, 116.0, 92.0, 16.0, 184.0, 18.60362975, 0.131156495, 22.0]],
    #   "index": [0,1]}}

    pdf_data = preprocess(json.loads(raw_data))

    # tabular data: {  "col1": [1,2,3], "col2": [2,3,4] }
    # log the raw input data
    # logging.info("data:{}".format(pdf_data))
    input_df = pd.DataFrame(pdf_data)

    # collect inputs data, store correlation_context
    context = inputs_collector.collect(input_df)

    # perform scoring with pandas Dataframe, return value is also pandas Dataframe
    predictions = model.predict(input_df.values)
    output_df = pd.DataFrame(predictions, columns=["PredictedLabel"])

    # collect outputs data, pass in correlation_context so inputs and outputs data can be correlated later
    outputs_collector.collect(output_df, context)

    # create a dataframe with inputs/outputs joined - this creates a URI folder (not mltable)
    # input_output_df = input_df.merge(output_df, context)
    input_output_df = input_df.join(output_df)

    # collect both your inputs and output
    inputs_outputs_collector.collect(input_output_df, context)

    return predictions.tolist()
