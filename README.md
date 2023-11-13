# From Hands-On to Automation: MLOps Implementation with Azure ML
**A Comprehensive Journey Covering CI/CD, Model Monitoring, and Retraining 🚀**

`#AzureML`, `#ml-ops`, `#automation`, `#data-drift`, `#model-drift`, `#managed-online-endpoints`, `#github-actions`, `#logic-apps`, `#solution-accelerator`

Welcome to this comprehensive guide on mastering MLOps! This repository is designed to address the challenges of implementing robust machine learning operations, providing you with a hands-on tutorial to navigate the complexities of model training, deployment, monitoring, and retraining.

The repository is structured around five detailed notebooks that guide you through the process of creating MLTable Datasets, training and deploying models, invoking endpoints, collecting data, creating and collecting synthetic data, and exploring collected data. These notebooks, located in the `notebooks` folder, offer a manual approach using the AzureML SDK or AzureML Studio UI.

We then delve into the power of the AzureML CLI, with YML definitions for data assets, compute resources, training pipelines, and deployment scripts for batch and online endpoints housed in the `pipelines`, `components`, `environments`, and `resources` folders.

Once a model is deployed, we introduce you to the AzureML datadrift monitor, a powerful tool for detecting drifts in data, data quality, or the model itself. This is crucial for maintaining the accuracy and reliability of your machine learning models over time.

Finally, we complete the MLOps cycle by automating training and deployment using GitHub Actions. These workflows, located under `.github\workflows\`, are triggered by AzureML Events from the Azure Event Grid, enabling seamless integration and automation of your MLOps.

This repository is more than just a guide; it's a comprehensive toolkit for your journey into the world of MLOps. Let's get started! 🎉

Note: A robust MLOps process in production necessitates a well-defined separation of development, testing, and production environments. This is where distinct AzureML Workspaces and the AzureML Registry come into play, providing a structured framework for managing these distinct environments. For a deeper dive into this topic, I highly recommend checking out [the Azure ML OPs v2 solution accelerator](https://github.com/Azure/mlops-v2).

## Prerequisites 📝

Before you start with this repository, it's important to ensure you have the following:

- **Knowledge**: Familiarity with AzureML, Azure CLI, and GitHub Actions is beneficial to fully understand and utilize this repository. If you're new to these tools, consider going through the following resources:
  - [AzureML Documentation](https://docs.microsoft.com/en-us/azure/machine-learning/)
  - [Azure CLI Documentation](https://docs.microsoft.com/en-us/cli/azure/)
  - [GitHub Actions Documentation](https://docs.github.com/en/actions)
- **Azure Subscription and Resource Group**: You'll need an Azure Subscription and Resource Group with sufficient permissions to create a service principal with contributor rights for this resource group, an AzureML Workspace including a Compute Instance to run both the notebooks and CLI commands, and Logic Apps.
- **GitHub Account**: A GitHub account is necessary so you can fork this repository and set up GitHub Actions.

Please ensure you meet these prerequisites before proceeding with the setup.

## Setup

### Setting up a Service Principal (SP)

Create a service principal with the `az ad sp create-for-rbac` command in the Azure CLI (e.g. run this command from your Compute Instance (CI) Terminal or with the Azure Cloud Shell in the Azure portal). Make sure to copy the JSON output as we will need it later.

```CLI
az ad sp create-for-rbac --name "cicd-monitor-demo" --role contributor --scopes /subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group> --sdk-auth
```

### Setting up GitHub Secrets

Fork this repository.

In GitHub, navigate to your repository.

Go to Settings in the navigation menu.

Select Security > Secrets and variables > Actions.

Select New repository secret.

Paste the entire JSON output from the Azure CLI command into the secret's value field. Give the secret the name AZURE_CREDENTIALS.

Select Add secret.

## ML Ops - A Step-by-Step Guide 📚

### Notebooks 📓

We'll begin with the most common approach - utilizing Jupyter Notebooks. This will allow us to fetch our data, train a Machine Learning model, and deploy it as an online endpoint. This can be done either via the SDK or manually from the AzureML Studio.

Depending on your preference, clone this repository onto your local machine or Azure Machine Learning Compute Instance.

- Execute each of the Jupyter notebooks (found in the 'notebooks' folder) and follow the instructions meticulously. Each notebook will provide a detailed explanation of the process.
- The initial notebook will generate demo data assets based on the Diabetes dataset.
- The subsequent notebook illustrates how to construct a training pipeline using the SDK, followed by deploying and monitoring a model on a Managed Online Endpoint.
- The third notebook shows how to invoke the endpoint while gathering production data.
- In the fourth notebook, we will fabricate synthetic data, simulating data drift.
- In the final notebook, we delve into the collected data from the endpoint.

### AzureML CLI 🛠️

#### Continuous Integration (CI) 🔄

Once the demo data assets, model, endpoint, and deployment are established, navigate to the `pipelines` and `components` directories. Here, you can compare the training pipeline experience with the SDK experience outlined in the second notebook.

From this point forward, we'll utilize this CI pipeline for retraining purposes. For instance, you can initiate this by running `az ml job create -f pipelines/ci_pipeline.yml`.

#### Continuous Deployment (CD) 🚀

With everything set up, we're now ready to deploy:

- The AzureML online endpoint can be deployed using the command `az ml online-endpoint create -f endpoints/online/endpoint/diabetes-endpoint.yml`.
- The model deployment (which includes production data collection) can be deployed using `az ml online-deployment create -f endpoints/online/deployment/diabetes-deployment-custom.yml`.

#### Monitoring 📊

Once we've gathered production data (for instance, by invoking the endpoint with production data from the first notebook), we can kick-start the monitoring of data and model drift. This can be achieved via `az ml schedule create -f "endpoints/online/monitor/01 - out-of-box monitor.yml"` or `az ml schedule create -f "endpoints/online/monitor/02 - advanced-model-monitoring.yml"`.

(_Optional_): For your convenience and to facilitate experimentation, we've included a straightforward Spark preprocessing component (`components\preprocess_production_data\`). This can be used for data and model drift detection using the `production data` we created in our notebooks, in case you prefer not to collect production data via an AzureML Online Endpoint Data Collector. The documentation provides detailed instructions on how to [monitor your own production data](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-monitor-model-performance?view=azureml-api-2&tabs=azure-cli#set-up-model-monitoring-by-bringing-your-own-production-data-to-azure-machine-learning).

### Automation via GitHub Actions 🤖

In the realm of MLOps, automation is key. We need to ensure that:

- Once we detect data or model drift, we automatically retrain the model. 🔄
- Once we register a new model, we automatically deploy it. 🚀

Bear in mind, this is a simplified overview. In a real-world scenario, you would likely have multiple workspaces and environments for development, testing, and production. This allows for evaluation of the best performing models before deployment, and possibly an approval process before deployment and retraining.

For best practices, refer to [the Azure ML OPs v2 solution accelerator](aka.ms/MLopsv2).

### Event Grid + Logic Apps 🌐

The workflow defined in `.github/workflows/cd-triggered-by-aml.yml` is designed to listen either to a manual dispatch (`workflow_dispatch`) or a webhook dispatch (`repository_dispatch`). It will then automatically deploy the model using the endpoint and deployment yaml files.

At this point, you only need to leverage the Azure Event Grid. We'll use a Logic App that is triggered by a `model registered` event and then runs a repository dispatch action on your cloned repository. To set up the Logic App, follow the process described [here](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-use-event-grid?view=azureml-api-2#example-send-email-alerts) to send an email alert (you could also create an [approval email](https://learn.microsoft.com/en-us/connectors/outlook/#send-approval-email)), then add a [GitHub Repository Dispatch Action](<https://learn.microsoft.com/en-us/connectors/github/#create-a-repository-dispatch-event-(preview)>)

Similarly, we can develop a second Logic App (or use some logic with conditionals) that listens to `data drift` events and triggers a CI repository dispatch for retraining a model.

Remember, this is a simplified process that provides you with the basic building blocks. For more comprehensive information and best practices, check [the Azure ML OPs v2 solution accelerator](aka.ms/MLopsv2).

## Wrapping Up 🎁

We hope this repository serves as a valuable resource in your journey towards mastering MLOps. The tools and practices outlined here are designed to help you navigate the complexities of machine learning operations, from model training and deployment to monitoring and retraining.

Remember, the world of MLOps is vast and constantly evolving. While this guide provides a solid foundation, we encourage you to continue exploring and learning. Stay curious, keep experimenting, and don't hesitate to dive deeper into the topics that interest you most.

Thank you for choosing this repository as your guide. We wish you all the best on your MLOps journey. Happy coding! 💻🚀
