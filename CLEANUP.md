# TODOS for cleanup

## MUST

### Part 1 - CI

- [x] Update Monitor
- [ ] Works with production-outputs but not with production?
- [x] Pipeline
  - [x] Adjust training pipeline
  - [x] Datasets
  - [x] Components
    - [x] prepare_data
      - [x] Rename
      - [x] Change input to mltable
      - [x] follow notebook cleaning steps
      - [x] change output to mltable
      - [x] Make use of random_state
      - [x] get rid of environment version string
        - [x] test
      - [x] Fix store_mltable
        - [x] parquet is not uploaded
        - [x] relative parquet path is wrong
          - [x] solve: solution is ugly
            - [x] test
          - [x] Solve: OSError: Cannot save file into a non-existent directory: '/mnt/azureml/cr/j/dc2508abf54c48c49e73137d83673775/cap/data-capability/wd/validation_data/validation_data'
            - [x] test
          - [ ] need an absolute path, not a relative path, to training-train mltable
            - [ ] ~~option 1~~
              - [ ] ~~convert train, val, test to urifile~~
              - [ ] ~~register train as mltable later~~
                - [ ] ~~is there a component for that?~~
            - [ ] option 2
              - [ ] get the absolute path somehow?
                - [ ] constructed the path. MLTable does not work properly with it.
            - [ ] option 3
              - [ ] use uri_file
    - [x] train
      - [x] update environment (latest)
      - [x] clean up
      - [x] test
      - [x] add test data
      - [x] test
    - [x] evaluate
      - [x] input mltable
      - [x] what to do with the deploy flag?
        - [x] Stores the result to a deploy_flag file and as a mlflow model metric
      - [x] Try using mlflow.sklearn instead of pyfunc
        - [x] It probably failed because evaluate used the wrong environment
          - [x] revert
        - [x] test
      - [x] switch to `validation_data`
      - [x] Fix: 'No numeric data to plot'
      - [x] test
    - [x] register
      - [x] Does it properly use the deploy flag?
      - [x] test
  - [x] Register training data output
  - [ ] Remove timestamp from features
    - [ ] Remove from monitor
      - [x] Update Monitor training data
        - [x] Use pipeline dataset output (training-train)
    - [ ] test
- [x] Environments
  - [x] Use 2023-10-09-15:45:00 for now
    - [x] replace with new env
- [ ] Update Status tag to 
  - [x] testing
  - [ ] production
- [x] Do we need all pipeline outputs?
  - [x] trained_model
  - [x] eval_output
  - [x] validation data?
  - [x] test

### Part 2 - CD

- [ ] Think about concept. Why deploy production to Managed Online Endpoints?
  - [ ] Explain in Readme
- [ ] Update Endpoints
- [ ] Update Deployments
- [ ] Update inference environment
- [ ] Update cd-triggered-by-aml

### Part 3 - CI/CD

- [ ] Update github workflows
- [ ] Fix event grid (run changed, not data drift detected)
  - [ ] ci-triggered-by-aml
    - [ ] repository_dispatch
      - [ ] datadrift event

### Part 4 - Monitor

## Should

- [ ] Remove all unused code
- [ ] Update Readme

## Could

- [ ] Update MoE Deployment
- [ ] Add Feature attribution drift: https://learn.microsoft.com/en-us/azure/machine-learning/reference-yaml-monitor?view=azureml-api-2#feature-attribution-drift
- [ ] Am I mixing up train, test, and validate and leaking old train data in new val data?
- [ ] Create a "simulate production" pipeline, that uses a recently trained model, runs prediction, and then registers the input-outputs dataset

## Would

- [ ] Use automl instead of random forest?
