resource "google_app_engine_application" "ts-appengine-app" {
  project       = var.gcp_project_id
  location_id      = var.gcp_region
}

resource "google_app_engine_application_url_dispatch_rules" "ts-appengine-app-dispatch-rules" {
  dispatch_rules {
    domain = "*"
    path = "/*"
    service = "default"
  }
}
