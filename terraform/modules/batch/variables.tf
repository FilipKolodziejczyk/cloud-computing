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