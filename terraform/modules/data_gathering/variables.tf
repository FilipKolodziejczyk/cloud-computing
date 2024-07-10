variable "gcp_project_id" {
  description = "The GCP project to deploy resources to"
  type        = string
}

variable "gcp_region" {
  description = "The GCP region to deploy resources to"
  type        = string
}

variable "data_providers" {
  description = "The data providers to deploy resources for"
  type        = list(string)
}

variable "cloud_function_source_dir" {
  description = "The directory containing the cloud function source code (each function should be in a separate subdirectory)"
  type        = string
}

variable "pubsub_real_time_topic" {
  description = "The Pub/Sub topic to publish real-time data to"
  type        = map(string)
}

variable "pubsub_batch_topic" {
  description = "The Pub/Sub topic to publish batch data to"
  type        = map(string)
}