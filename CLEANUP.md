# TODOS for cleanup

## MUST

- Done

## Should

- [x] Remove all unused code
- [ ] Update Readme
- [ ] Use the correct training data in Monitoring

## Could

~~- [ ] Update MoE Deployment~~
- [ ] Add Feature attribution drift: https://learn.microsoft.com/en-us/azure/machine-learning/reference-yaml-monitor?view=azureml-api-2#feature-attribution-drift
- [x] Am I mixing up train, test, and validate and leaking old train data in new val data?
- [ ] Create a "simulate production" pipeline, that uses a recently trained model, runs prediction, and then registers the input-outputs dataset

## Would

- [ ] Use automl instead of random forest?
- [ ] Add RAI Dashboard
  - [ ] https://github.com/Azure/RAI-vNext-Preview
