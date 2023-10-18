# mlops-ci-cd-monitor-retrain

End-to-end demo for an AzureML ML Ops pipeline.

## Setup

Fork this repository.

Create a service principal with the `az ad sp create-for-rbac` command in the Azure CLI (e.g. run this command with Azure Cloud Shell in the Azure portal).

```CLI
az ad sp create-for-rbac --name "cicd-monitor-demo" --role contributor --scopes /subscriptions/13c1109b-ba76-4ca6-8161-8767bdf3c75c/resourceGroups/ai-services-rg --sdk-auth
```

In GitHub, go to your repository.

Go to Settings in the navigation menu.

Select Security > Secrets and variables > Actions.

Select New repository secret.

Paste the entire JSON output from the Azure CLI command into the secret's value field. Give the secret the name AZURE_CREDENTIALS.

Select Add secret.

## Creating the demo

### Notebooks

Depending on where you want to run your code, clone this repository onto your local machine or Azure Machine Learning Compute Instance.

Run each of the Jupyter notebooks (located in the 'notebooks' folder) and follow the instructions step by step. Each notebook will explain the process in detail.

- The first notebook will create demo data assets based on the Diabetes dataset.
- The second notebook demonstrates how to create a training pipeline using the SDK, and then deploy and monitor a model on an Managed Online Endpoint.
- The third notebook demonstrates how to invoke the endpoint while collecting production data.
- In the fourth notebook we will create synthetic data (= data drift)
- In the last notebook we explore the collected data from the endpoint.

### AzureML CLI

#### CI

Once the demo data assets, model, endpoint, and deployment are in place, go to 'pipelines' and 'components' and compare the training pipeline experience with the SDK experience from the second notebook.

We will use this ci_pipeline from now on for retraining, e.g. by running `az ml job create -f pipelines/ci_pipeline.yml`.

#### CD

We can now deploy

- the endpoint via `az ml online-endpoint create -f endpoints/online/endpoint/diabetes-endpoint.yml`
- the model deployment (including production data collection) via `az ml online-deployment create -f endpoints/online/deployment/diabetes-deployment-custom.yml`

#### Monitoring

Once we collect produciton data (e.g. by invoking the endpoint with production data from the first notebook) we can start monitor the data and model drift via `az ml schedule create -f "endpoints/online/monitor/01 - out-of-box monitor.yml"` or `az ml schedule create -f "endpoints/online/monitor/02 - advanced-model-monitoring.yml"`

### Automation via GitHub Actions

For ML Ops we'll need to automate our processes, so that

- once we detect data or model drift, we retrain the model.
- once we register a new model, we deploy the model automatically.

Of course this is a simplification, as you will want

- multiple workspaces and environments for dev, test, and production
- evaluation of the best performing models before deployment
- an approval process before deployment and possibly retraining.

For best practices check [aka.ms/**MLopsv2**](https://github.com/Azure/mlops-v2)

#### Event Grid + Logic Apps

The workflow defined in .github/workflows/cd-triggered-by-aml.yml will listen either to a manual dispatch (workflow_dispatch) or a webhook dispatch (repository_dispatch) and automatically deploy the model using the endpoint and deployment yaml files.

You will now only need to leverage the Azure Event Grid. Therefore we'll use a Logic App, that is triggered by a model registered event and then runs a repository dispatch action on your cloned repository. The process is described [here](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-use-event-grid?view=azureml-api-2).

In a similar manner, we can develop a second Logic App (or use some logic with conditionals) that listens to data drift events and triggers a CI repository dispatch for retraining a model.

Again, this is a very simplified process, that shows you the basic building blocks. For more information and best practices check [aka.ms/**MLopsv2**](https://github.com/Azure/mlops-v2).
