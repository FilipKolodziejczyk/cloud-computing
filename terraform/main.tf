terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.26.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "5.26.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_zone
}

provider "google-beta" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_zone
}

variable "google_apis" {
  default = [
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudscheduler.googleapis.com",
    "run.googleapis.com",
    "firestore.googleapis.com",
    "bigtable.googleapis.com",
    "looker.googleapis.com",
    "dataflow.googleapis.com",
    "identitytoolkit.googleapis.com",
    "eventarc.googleapis.com"
  ]
}

resource "google_project_service" "google_apis" {
  for_each = toset(var.google_apis)

  project = var.gcp_project_id
  service = each.key
}

resource "google_artifact_registry_repository" "workflow_repo" {
  depends_on = [google_project_service.google_apis]

  project       = var.gcp_project_id
  location      = var.gcp_region
  description   = "Repository for storing dataflow flex templates"
  format        = "DOCKER"
  repository_id = "workflow-repo"
}

module "data_gathering" {
  depends_on = [google_project_service.google_apis]

  source                    = "./modules/data_gathering"
  gcp_project_id            = var.gcp_project_id
  gcp_region                = var.gcp_region
  data_providers            = var.data_providers
  cloud_function_source_dir = var.cloud_function_source_dir
  pubsub_real_time_topic    = module.real_time.data_provider_topic_real_time
  pubsub_batch_topic        = module.batch.data_provider_topic_batch
}

module "real_time" {
  depends_on = [google_project_service.google_apis]
  source         = "./modules/real_time"
  gcp_project_id = var.gcp_project_id
  gcp_region     = var.gcp_region
  gcp_zone       = var.gcp_zone
  data_providers = var.data_providers
}

module "batch" {
  depends_on = [google_project_service.google_apis]

  source         = "./modules/batch"
  gcp_project_id = var.gcp_project_id
  gcp_region     = var.gcp_region
  gcp_zone       = var.gcp_zone
  data_providers = var.data_providers
}
