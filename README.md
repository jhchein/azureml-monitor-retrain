# mlops-ci-cd-monitor-retrain

End-to-end demo for a mlops pipeline

Create a service principal with the az ad sp create-for-rbac command in the Azure CLI. Run this command with Azure Cloud Shell in the Azure portal or by selecting the Try it button.

```CLI
az ad sp create-for-rbac --name "cicd-monitor-demo" --role contributor --scopes /subscriptions/13c1109b-ba76-4ca6-8161-8767bdf3c75c/resourceGroups/ai-services-rg --sdk-auth
```

In GitHub, go to your repository.

Go to Settings in the navigation menu.

Select Security > Secrets and variables > Actions.

Select New repository secret.

Paste the entire JSON output from the Azure CLI command into the secret's value field. Give the secret the name AZURE_CREDENTIALS.

Select Add secret.

---

az ml online-endpoint invoke --name clr-diabetes-jhch-demo --deployment-name cli-deployment --subscription 13c1109b-ba76-4ca6-8161-8767bdf3c75c --resource-group ai-services-rg --workspace-name schaeffler-ops-it-aml --request-file "C:\code\mlops-ci-cd-monitor-retrain\test.json"
