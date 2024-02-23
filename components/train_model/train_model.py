from argparse import ArgumentParser

import mlflow
import mltable
import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.tree import DecisionTreeClassifier


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--train_data", type=str, dest="train_data", required=True)
    parser.add_argument(
        "--validation_data", type=str, dest="validation_data", required=True
    )
    parser.add_argument(
        "--trained_model", type=str, dest="trained_model", required=True
    )
    args = parser.parse_args()

    lines = [
        f"Train data path: {args.train_data}",
        f"validation data path: {args.validation_data}",
        f"Trained model path: {args.trained_model}",
    ]

    for line in lines:
        print(line)

    return args


def log_metrics(y, yhat):
    accuracy = accuracy_score(y, yhat)
    f1 = f1_score(y, yhat)
    recall = recall_score(y, yhat)
    precision = precision_score(y, yhat)
    roc_auc = roc_auc_score(y, yhat)

    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1", f1)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("roc_auc", roc_auc)


def log_confusion_matrix(y, yhat):
    # plotting the confusion matrix
    cm = confusion_matrix(y, yhat)
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


def load_data(data_path: str):
    tbl = mltable.load(data_path)
    df = tbl.to_pandas_dataframe()
    return df.drop(columns=["failure"]), df["failure"]


def main(args):
    X_train, y_train = load_data(args.train_data)
    X_val, y_val = load_data(args.validation_data)

    model = DecisionTreeClassifier().fit(X_train, y_train)
    mlflow.log_param("model", type(model).__name__)

    yhat_val = model.predict(X_val)

    log_metrics(y_val, yhat_val)
    log_confusion_matrix(y_val, yhat_val)

    mlflow.sklearn.save_model(
        sk_model=model,
        path=args.trained_model,
    )


if __name__ == "__main__":
    mlflow.start_run()

    args = parse_args()

    main(args)

    mlflow.end_run()
