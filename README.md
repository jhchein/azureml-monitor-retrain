# ML Ops - Monitoring Models and Data with Azure ML

The repository provides you a quick start to develop your own model and data monitoring using the latest AzureML Monitoring.

As using  monitoring in combination with managed online endpoints is very straightforward, this quickstart focuses on the **bring your own production data** scenario, meaning that we will use production data that logged anywhere except Managed Online Endpoints.

## Prerequisites

- **Knowledge**: This guide expects you to be familar with AzureML and Azure CLI. Knowledge about GitHub Actions is optional, but essential to fully utilize this repository for automation. If you're new to these tools, consider going through the following resources:
  - [AzureML Documentation](https://docs.microsoft.com/en-us/azure/machine-learning/)
  - [Azure CLI Documentation](https://docs.microsoft.com/en-us/cli/azure/)
  - [GitHub Actions Documentation](https://docs.github.com/en/actions)
- **Azure Subscription and Resource Group**: You'll need
  - an Azure Subscription and a Resource Group
  - permissions to create a service principal with contributor rights for the resource group
  - an AzureML Workspace including a Compute Instance to run both the notebooks and CLI commands, and Logic Apps.
- **GitHub Account (optional)**: A GitHub account is necessary for automated retraining. You can then fork this repository and set up GitHub Actions.

## Step 0 - Setup

We will use a Compute Instance to run the notebooks and CLI commands.

- Start your compute instance and connect to the terminal of your compute instance (see: [Access a compute instance terminal in your workspace](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-access-terminal?view=azureml-api-2))
- Update your AzureML CLI extension via `az extension update -n ml`
- Navigate to the location where you would like to clone the repository, e.g. `/users/<your_username>/`.
- Clone this repository via `git clone https://github.com/jhchein/azureml-monitor-retrain.git`
- Navigate to the newly created directory (e.g. via `cd azureml-monitor-retrain`).

## Step 1 - Monitoring

### Data and Model Preparation

The two notebooks `00 - Prepare Data Assets.ipynb` and `01 - Train and Deploy.ipynb`, found under `notebooks`, guide you through the process of creating a synthetic dataset and manually training a model.

- Open the two notebooks in your AzureML Studio UI under `Notebooks` and execute them using the `AzureML_py310_sdkv2` Kernel. (see: [Run Jupyter notebooks in your workspace](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-run-jupyter-notebooks?view=azureml-api-2))
- (optional): Once the notebooks are executed, you could follow the documentation to deploy the model to a Managed Online Endpoint, set up monitoring via the UI, and run inference against the production data.

### Setup AzureML Monitoring

#### Preprocessing

AzureML Monitoring requires a Spark Component to translate production data (from a Uri_folder) to a relational format (mltable). We will need to register a preprocessing component.

- Investigate and familiarize yourself with `components/preprocess_synthetic_data/preprocess_synthetic_data.yml`. For reference you can use the [CLI (v2) Spark component YAML schema](https://learn.microsoft.com/en-us/azure/machine-learning/reference-yaml-component-spark?view=azureml-api-2).
- Register the component via `az ml component create -f components/preprocess_synthetic_data/preprocess_synthetic_data.yml` (see [Azure CLI Reference](https://learn.microsoft.com/en-us/cli/azure/ml/component?view=azure-cli-latest#az-ml-component-create))

#### Scheduling the Monitor 📊

We can now implement the monitor:

- Familiarize yourself with `schedule/monitor/bring-your-own-data/01 - synthetic-data.yml` and then update `alert_notification/emails` (at the bottom of the file) with your own email adress. For reference you can check the [YAML schema for model monitoring](https://learn.microsoft.com/en-us/azure/machine-learning/reference-yaml-monitor?view=azureml-api-2).
- In your Compute Instance Terminal deploy the schedule using `az ml schedule create --file './schedule/monitor/bring-your-own-data/01 - synthetic-data.yml'`
- Examine the monitor in your AzureML Studio. Manually trigger the first run, wait, and then explore the monitoring metrics.

## Step 2 - Automation with the AzureML CLI 🛠️

Now that the monitor is in place, we can focus on automatically retraining the model.

### Create Training Environment

Model training has dependencies, for example Machine Learning Frameworks such as scikit-learn, pytorch or tensorflow. We will need to create a stable environment to train the model.

- Familiarize yourself with the training environment definition `environments/sklearn-with-mltable.yml` (which defines the environment and base image) and `environments/sklearn-with-mltable/conda_dependencies.yaml` (definining the conda dependencies required to train the model).
- In your Compute Instance Terminal execute: `az ml environment create --file environments/sklearn-with-mltable.yml`

### Continuous Integration (CI) 🔄

Now that the environment is created, we can automate the training process we had used in notebook `01 - Train and Deploy.ipynb`.

- Familiarize yourself and then update `pipelines/ci-synthetic.yml`.
- Also make sure to inspect and understand the components we use, provided in the  `components` directory. Here, you can compare the training pipeline experience with the SDK experience outlined in the second notebook.

From this point forward, we'll utilize this CI pipeline for retraining purposes. For instance, you can initiate this by running `az ml job create -f pipelines/ci_pipeline.yml --stream` and then follow the streaming link to examine the training progress in the AzureML Studio UI.

### Setting up a Service Principal (SP)

Create a service principal with the `az ad sp create-for-rbac` command in the Azure CLI (e.g., run this command from your Compute Instance (CI) Terminal or with the Azure Cloud Shell in the Azure portal). Make sure to copy the JSON output as we will need it later.

`az ad sp create-for-rbac --name "cicd-monitor-demo" --role contributor --scopes /subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group> --sdk-auth`

### Setting up GitHub Secrets

Fork this repository.

In GitHub, navigate to your repository.

Go to Settings in the navigation menu.

Select Security > Secrets and variables > Actions.

Select New repository secret.

Paste the entire JSON output from the Azure CLI command into the secret's value field. Give the secret the name AZURE_CREDENTIALS.

Select Add secret.

### Automation via GitHub Actions 🤖

In the realm of MLOps, automation is key. We need to ensure that:

- Once we detect data or model drift, we automatically retrain the model. 🔄
- Once we register a new model, we automatically deploy it. 🚀

Therefore, the CI workflow defined in `.github/workflows/cd-triggered-by-aml.yml` is designed to listen either to a manual dispatch (`workflow_dispatch`) or a webhook dispatch (`repository_dispatch`). It will then automatically deploy the model using the endpoint and deployment YAML files.

If you use Managed Online Endpoints, continuous deployment is very straightforward. In contrast, we chose to deploy the model somewhere else in this scenario. We need to set up our own deployment pipeline, and the code is not provided.

> Note: Bear in mind, this is a simplified overview. In a real-world scenario, you would likely have multiple workspaces and environments for development, testing, and production. This allows for evaluation of the best-performing models before deployment, and possibly an approval process before deployment and retraining. For best practices, refer to [the Azure ML Ops v2 solution accelerator](aka.ms/MLopsv2).

### Event Grid + Logic Apps 🌐

At this point, you only need to leverage the Azure Event Grid.

We'll use a Logic App that is triggered by a `run status change` event, filter for `data.RunTags.azureml_modelmonitor_threshold_breached`, and then runs a repository dispatch action on your forked repository.

To set up the Logic App, follow the process described [here](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-use-event-grid?view=azureml-api-2#example-send-email-alerts) to send an email alert (you could also create an [approval email](https://learn.microsoft.com/en-us/connectors/outlook/#send-approval-email)), then add a [GitHub Repository Dispatch Action](https://learn.microsoft.com/en-us/connectors/github/#create-a-repository-dispatch-event-(preview)). Consider writing the [email to a Teams channel](https://support.microsoft.com/en-us/office/send-an-email-to-a-channel-in-microsoft-teams-d91db004-d9d7-4a47-82e6-fb1b16dfd51e), it will appear as a message.

This [guide](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-monitor-model-performance?view=azureml-api-2&tabs=azure-cli#integrate-azure-machine-learning-model-monitoring-with-azure-event-grid) explains the details, how to configure the necessary data drift event filtering steps in depth

Similarly, if you created a CD pipeline and GitHub Action, we can develop a second Logic App (or use some logic with conditionals) that listens to `model registered` events and triggers a CI repository dispatch for retraining a model.

Remember, this is a simplified process that provides you with the basic building blocks. For more comprehensive information and best practices, check [the Azure ML OPs v2 solution accelerator](https://github.com/Azure/mlops-v2).

## Wrapping Up 🎁

I hope this repository serves as a valuable resource in your journey towards implementing MLOps. The tools and practices outlined here are designed to help you navigate the complexities of machine learning operations, from model training and deployment to monitoring and retraining.

Thank you for choosing this repository as your guide. I wish you all the best on your MLOps journey. Happy coding! 💻🚀
