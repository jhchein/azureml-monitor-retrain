# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Evaluates trained ML model using test dataset.
Saves predictions, evaluation results and deploy flag.
"""

import argparse
import os
from pathlib import Path

import mlflow
import mlflow.pyfunc
import mlflow.sklearn
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from mlflow.tracking import MlflowClient
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def parse_args():
    """Parse input arguments"""

    parser = argparse.ArgumentParser("predict")
    parser.add_argument("--model_name", type=str, help="Name of registered model")
    parser.add_argument("--model_input", type=str, help="Path of input model")
    parser.add_argument(
        "--test_data",
        dest="test_data",
        type=str,
        help="Path to test dataset (uri_file, data.parquet)",
    )
    parser.add_argument(
        "--evaluation_output",
        type=str,
        help="Path to store the eval results (score.txt)",
    )
    parser.add_argument(
        "--runner", type=str, help="Local or Cloud Runner", default="CloudRunner"
    )

    args = parser.parse_args()

    return args


def main(args):
    """Read trained model and test dataset, evaluate model and save result"""

    df = pd.read_parquet(args.test_data)
    X, y = df.drop(columns=["failure"]), df["failure"]

    # Load the model from input port
    model = mlflow.pyfunc.load_model(args.model_input)

    # ---------------- Model Evaluation ---------------- #
    yhat, score = model_evaluation(X, y, model, args.evaluation_output)

    # ----------------- Model Promotion ---------------- #
    if args.runner == "CloudRunner":
        predictions, deploy_flag = model_promotion(
            args.model_name, args.evaluation_output, X, y, yhat, score
        )


def model_evaluation(X_test, y_test, model, evaluation_output):
    if not os.path.exists(evaluation_output):
        os.makedirs(evaluation_output)
    # Get predictions to y_test (y_test)
    yhat_test = model.predict(X_test)

    # Save the output data with feature columns, predicted cost, and actual cost in csv file
    output_data = X_test.copy()
    output_data["real_label"] = y_test
    output_data["predicted_label"] = yhat_test
    output_data.to_csv((Path(evaluation_output) / "predictions.csv"))

    # Evaluate Model performance with the test set
    acc_test = accuracy_score(y_test, yhat_test)
    f1_test = f1_score(y_test, yhat_test)
    recall_test = recall_score(y_test, yhat_test)
    precision_test = precision_score(y_test, yhat_test)
    roc_auc_test = roc_auc_score(y_test, yhat_test)

    # Print score report to a text file
    (Path(evaluation_output) / "score.txt").write_text(
        f"Scored with the following model:\n{format(model)}"
    )
    with open((Path(evaluation_output) / "score.txt"), "a") as outfile:
        outfile.write(f"Accuracy: {acc_test:.2f} \n")
        outfile.write(f"F1 score: {f1_test:.2f} \n")
        outfile.write(f"Recall: {recall_test:.2f} \n")
        outfile.write(f"Precision: {precision_test:.2f} \n")
        outfile.write(f"ROC AUC: {roc_auc_test:.2f} \n")

    # Log metrics
    mlflow.log_metric("accuracy", acc_test)
    mlflow.log_metric("f1", f1_test)
    mlflow.log_metric("recall", recall_test)
    mlflow.log_metric("precision", precision_test)
    mlflow.log_metric("roc_auc", roc_auc_test)

    # plotting the confusion matrix
    cm = confusion_matrix(y_test, yhat_test)
    plt.clf()
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Wistia)
    classNames = ["Negative", "Positive"]
    plt.title("Diabetes Confusion Matrix - Training Set")
    plt.ylabel("True label")
    plt.xlabel("Predicted label")
    tick_marks = np.arange(len(classNames))
    plt.xticks(tick_marks, classNames, rotation=45)
    plt.yticks(tick_marks, classNames)

    # save confusion matrix to confusion_matrix.png
    plt.savefig("confusion_matrix.png", format="png")

    mlflow.log_artifact("confusion_matrix.png")

    return yhat_test, f1_test


def model_promotion(model_name, evaluation_output, X_test, y_test, yhat_test, score):
    """The model_promotion function is responsible for deciding whether the
    current model should be promoted (deployed) or not. This decision is based
    on the F1 score of the current model compared to the F1 scores of previous
    versions of the model.

    The function also logs the deploy flag, the performance comparison plot,
    and the confusion matrix plot.

    The deploy flag is saved to a file called deploy_flag in the evaluation
    output directory. The performance comparison plot is saved to a file called
    perf_comparison.png in the evaluation output directory. The confusion
    matrix plot is saved to the MLflow artifact store.

    Args:
        model_name (str): Name of the sklearn model
        evaluation_output (str): Path to store the eval results (score.txt)
        X_test (pandas DataFrame): Test dataset
        y_test (pandas Series): Test labels
        yhat_test (pandas Series): Predicted labels
        score (float): F1 score of the current model

    Returns:
        dict: Predictions of the current and previous versions of the model
        int: Deploy flag (1: deploy, 0: do not deploy)
    """
    scores = {}
    predictions = {}

    client = MlflowClient()

    for model_run in client.search_model_versions(f"name='{model_name}'"):
        model_version = model_run.version
        mdl = mlflow.pyfunc.load_model(
            model_uri=f"models:/{model_name}/{model_version}"
        )
        predictions[f"{model_name}:{model_version}"] = mdl.predict(X_test)
        scores[f"{model_name}:{model_version}"] = f1_score(
            y_test, predictions[f"{model_name}:{model_version}"]
        )

    if scores:
        if score >= max(list(scores.values())):
            deploy_flag = 1
            print(f"Score: {score} greater than {max(list(scores.values()))}")
        else:
            deploy_flag = 0
            print(f"Score: {score} less than {max(list(scores.values()))}")
    else:
        deploy_flag = 1
        print("No previous model to compare with.")

    print(f"Deploy flag: {deploy_flag}, the model will be deployed.")

    with open((Path(evaluation_output) / "deploy_flag"), "w") as outfile:
        outfile.write(f"{int(deploy_flag)}")

    # add current model score and predictions
    scores["current model"] = score
    predictions["current model"] = yhat_test

    perf_comparison_plot = pd.DataFrame(scores, index=["f1 score"]).plot(
        kind="bar", figsize=(15, 10)
    )
    perf_comparison_plot.figure.savefig("perf_comparison.png")
    perf_comparison_plot.figure.savefig(Path(evaluation_output) / "perf_comparison.png")

    mlflow.log_metric("deploy flag", bool(deploy_flag))
    mlflow.log_artifact("perf_comparison.png")

    return predictions, deploy_flag


if __name__ == "__main__":
    mlflow.start_run()

    args = parse_args()

    lines = [
        f"Model name: {args.model_name}",
        f"Model path: {args.model_input}",
        f"Test data path: {args.test_data}",
        f"Evaluation output path: {args.evaluation_output}",
    ]

    for line in lines:
        print(line)

    main(args)

    mlflow.end_run()
