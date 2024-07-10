resource "google_bigquery_dataset" "batch-dataset" {
  project    = var.gcp_project_id
  dataset_id = "batch_dataset"
  location   = var.gcp_region
}

resource "google_project_iam_member" "looker-bigquery-read-only" {
  project = var.gcp_project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:looker@${var.gcp_project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "looker-bigquery-job-user" {
  project = var.gcp_project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:looker@${var.gcp_project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "looker-bigquery-metadata-viewer" {
  project = var.gcp_project_id
  role    = "roles/bigquery.metadataViewer"
  member  = "serviceAccount:looker@${var.gcp_project_id}.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "looker-bigquery-user" {
  project = var.gcp_project_id
  role    = "roles/bigquery.user"
  member  = "serviceAccount:looker@${var.gcp_project_id}.iam.gserviceaccount.com"
}

resource "google_service_account" "looker" {
  account_id   = "looker"
  project      = var.gcp_project_id
  display_name = "Looker Service Account"
}

resource "google_service_account_key" "looker" {
  service_account_id = google_service_account.looker.id
}

#resource "google_identity_platform_oauth_idp_config" "oauth_idp_config" {
#  name          = "oidc.oauth-idp-config"
#  display_name  = "OIDC IDP Config"
#  client_id     = "client-id"
#  issuer        = "issuer"
#  enabled       = true
#  client_secret = "secret"
#}

#resource "google_looker_instance" "looker-instance" {
#  project          = var.gcp_project_id
#  name             = "looker-instance"
#  platform_edition = "LOOKER_CORE_STANDARD_ANNUAL"
#  region           = var.gcp_region
#
#
#  oauth_config {
#    client_id     = google_identity_platform_oauth_idp_config.oauth_idp_config.client_id
#    client_secret = google_identity_platform_oauth_idp_config.oauth_idp_config.client_secret
#  }
#}


