# Cloud Computing project: Multi-Provider Weather Forecasting and Analysis

The goal of this project is to create a system in GCP, with strong emphasis of using the cloud-native services provided by the platform. The system will be able to provide weather forecasting and analysis, combining data from multiple providers. It is a way to compare or combine the data from different providers, and to provide a more reliable forecast. There will be two main user interfaces: a web app with real-time forecasting and a BI tool for historical data analysis. The system should be able to scale according to the demand, including large scale scenarios.

## Architecture Overview

![Architecture](/architecture.png)

All of the components are virtually infinite scalable, with the exception of the BigTable, when set to proper configuration. Therefore, it is capable to handle huge amounts of data and requests. The system is also meant to be highly available, once again, if properly configured.

## SLA, SLO, SLI

| Service | SLO (% availability) | SLA |
| --- | --- | --- |
| OpenWeatherAPI | 95 | &cross; |
| OpenWeatherAPI (Enterprise) | 99.95 | &check; |
| Open-Meteo | 99.9 | &cross; |
| Open-Meteo (Enterprise) | 99.9 | &check; |
| Cloud Functions | 99.95 | &check; |
| Cloud Scheduler | 99.5 | &check; |
| Pub/Sub | 99.95 | &check; |
| Firestore (Regional) | 99.99 | &check; |
| Dataflow | 99.9 | &check; |
| BigTable (single cluster) | 99.9 | &check; |
| BigQuery | 99.9 | &check; |
| App Engine | 99.95 | &check; |
| Data Looker (standard) | 99.5 | &check; |
| Cloud Logging | 99.95 | &check; |
| Cloud Monitoring | 99.95 | &check; |

To estimate SLO of whole infrastructure, we could use probability theory (product of sequential components). However, it still would not capture the whole picture, as it is only infrastructure, without the application itself. To estimate that, we would have to define SLIs and measure them with proper tools.

## Terraform setup

Initial setup:

1. Install Google Cloud SDK: [manual](https://cloud.google.com/sdk/docs/install-sdk)
2. Install Terraform: [manual](https://learn.hashicorp.com/tutorials/terraform/install-cli)
3. Authenticate with Google Cloud SDK: `gcloud auth login`
4. Create a new project: `gcloud projects create <project-id>`
5. Set the project: `gcloud config set project <project-id>`
6. Create a 'terraform/terraform.tfvars' file so it will match the 'terraform/variables.tf' file. Example:

```bash
project_id = "<project-id>"
region = "<region>"
...
```

8. Run `terraform init` to initialize the Terraform configuration.

## Terraform usage

1. Run `terraform validate` to validate the configuration.
2. Run `terraform fmt` to format the configuration.
3. Run `terraform plan` to see the changes that will be applied.
4. Run `terraform apply` to apply the changes.
5. Run `terraform destroy` to destroy the infrastructure.