resource "google_firestore_database" "data_gathering_firestore" {
  provider    = google-beta
  project     = var.gcp_project_id
  name        = "default"
  location_id = var.gcp_region
  type        = "FIRESTORE_NATIVE"
}
