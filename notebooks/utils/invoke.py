import json
import os
import ssl
import requests


def allow_self_signed_https(allowed):
    """
    Bypasses the server certificate verification on the client side if using a self-signed certificate.
    """
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context


def invoke_endpoint(url, deployment, api_key, payload):
    """
    Invokes an Azure ML endpoint with the specified URL, deployment name, and API key.
    If x_new is not provided, generates new data to use in querying.
    """
    allow_self_signed_https(True)

    # # Generate new data to use in querying if x_new is not provided
    # if x_new is None:
    #     x_new = [[2,180,74,24,21,23.9091702,1.488172308,22],
    #             [4,96,83,26,34,52.94533137,0.160199188,53],
    #             [1,125,83,41,235,19.65795152,0.150529189,23],
    #             [3,106,83,39,223,31.77645097,0.877332438,22],
    #             [0,148,58,11,179,39.19207553,0.160829008,45]]

    # # Construct the request body based on the deployment type
    # if deployment == "cli-deployment":
    #     data = {
    #         "input_data": {
    #             "data": x_new,
    #             "columns": ["Pregnancies", "PlasmaGlucose", "DiastolicBloodPressure", "TricepsThickness", "SerumInsulin", "BMI", "DiabetesPedigree", "Age"],
    #             "index": [0,1,2,3,4]
    #         }
    #     }
    # elif deployment in ["ui-deployment", "notebook-deployment"]:
    #     data = {"input_data": x_new}
    # else:
    #     raise ValueError("Invalid deployment name")

    # Encode the request body as JSON and set the request headers
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "azureml-model-deployment": deployment
    }

    # Send the request and handle any errors
    # try:
    response = requests.post(url, data=body, headers=headers)
    response.raise_for_status()
    predicted_classes = response.json()
    return predicted_classes
    # for i in range(len(pay)):
    #     print(f"Patient {x_new[i]}: {predicted_classes[i]}")

    # except requests.exceptions.HTTPError as error:
    #     print(f"The request failed with status code: {error.response.status_code}")
    #     print(error.response.text)

    # except requests.exceptions.RequestException as error:
    #     print(f"An error occurred while making the request: {error}")