from argparse import ArgumentParser

import mlflow
import pandas as pd
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
        "--trained_model", type=str, dest="trained_model", required=True
    )
    args = parser.parse_args()
    return args


def main(args):
    train_dataset = pd.read_parquet(args.train_data)
    y_train = train_dataset["Diabetic"]
    X_train = train_dataset[
        [
            "Pregnancies",
            "PlasmaGlucose",
            "DiastolicBloodPressure",
            "TricepsThickness",
            "SerumInsulin",
            "BMI",
            "DiabetesPedigree",
            "Age",
        ]
    ]

    model = DecisionTreeClassifier().fit(X_train, y_train)
    mlflow.log_param("model", "DecisionTreeClassifier")

    yhat_train = model.predict(X_train)
    acc_train = accuracy_score(y_train, yhat_train)
    f1_train = f1_score(y_train, yhat_train)
    recall_train = recall_score(y_train, yhat_train)
    precision_train = precision_score(y_train, yhat_train)
    roc_auc_train = roc_auc_score(y_train, yhat_train)

    mlflow.log_metric("accuracy", acc_train)
    mlflow.log_metric("f1", f1_train)
    mlflow.log_metric("recall", recall_train)
    mlflow.log_metric("precision", precision_train)
    mlflow.log_metric("roc_auc", roc_auc_train)

    # plotting the confusion matrix
    cm = confusion_matrix(y_train, yhat_train)
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

    mlflow.sklearn.save_model(
        sk_model=model,
        path=args.trained_model,
    )


if __name__ == "__main__":
    mlflow.start_run()

    args = parse_args()

    lines = [
        f"Train data path: {args.train_data}",
        f"Trained model path: {args.trained_model}",
    ]

    for line in lines:
        print(line)

    main(args)

    mlflow.end_run()
