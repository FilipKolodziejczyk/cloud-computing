variable "gcp_project_id" {
  description = "The GCP project to deploy resources to"
  type        = string
}

variable "gcp_region" {
  description = "The GCP region to deploy resources to"
  type        = string
}

variable "gcp_zone" {
  description = "The GCP zone to deploy resources to"
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