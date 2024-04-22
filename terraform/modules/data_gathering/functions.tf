resource "google_service_account" "cloud_function_sa" {
  project      = var.gcp_project_id
  account_id   = "cloud-function-sa"
  display_name = "Cloud Function Service Account"
}

resource "google_storage_bucket" "cloud_function_source_bucket" {
  project                     = var.gcp_project_id
  name                        = "${var.gcp_project_id}-cloud-function-source-bucket"
  location                    = var.gcp_region
  uniform_bucket_level_access = true
}

resource "null_resource" "zip_sources" {
  for_each = toset(var.data_providers)

  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = <<EOH
      mkdir ${path.root}/artifacts && \ 
      cp -r ${path.root}/${var.cloud_function_source_dir}/${each.value}-func/* ${path.root}/artifacts/ && \
      cd ${path.root}/artifacts/ && \
      zip -r ${each.value}.zip .
    EOH
  }
}

resource "google_storage_bucket_object" "cloud_function_source" {
  depends_on = [null_resource.zip_sources]

  for_each = toset(var.data_providers)

  name   = "${each.value}.zip"
  bucket = google_storage_bucket.cloud_function_source_bucket.name
  source = "${path.root}/artifacts/${each.value}.zip"
}

resource "google_cloudfunctions2_function" "data_gathering_function" {
  for_each = toset(var.data_providers)

  project     = var.gcp_project_id
  name        = "${lower(each.value)}-data-gathering-function"
  description = "Data gathering function for ${each.value}"
  location    = var.gcp_region

  build_config {
    runtime     = "python312"
    entry_point = "cloud_function_entry_point"
    source {
      storage_source {
        bucket = google_storage_bucket.cloud_function_source_bucket.name
        object = google_storage_bucket_object.cloud_function_source[each.value].name
      }
    }
  }

  service_config {
    available_memory      = "256Mi"
    min_instance_count    = 1
    max_instance_count    = 5
    timeout_seconds       = 120
    service_account_email = google_service_account.cloud_function_sa.email
    environment_variables = {
      GCP_PROJECT_ID          = var.gcp_project_id
      PUBSUB_TOPIC_ID         = var.pubsub_real_time_topic[each.key]
      PUBSUB_BATCH_TOPIC_ID   = var.pubsub_batch_topic[each.key]
      FIRESTORE_DATABASE_NAME = google_firestore_database.data_gathering_firestore.name
      FIRESTORE_COLLECTION_ID = each.value
    }
  }
}

resource "google_cloudfunctions2_function_iam_member" "invoker" {
  for_each = toset(var.data_providers)

  project        = var.gcp_project_id
  location       = google_cloudfunctions2_function.data_gathering_function[each.key].location
  cloud_function = google_cloudfunctions2_function.data_gathering_function[each.key].name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${google_service_account.cloud_function_sa.email}"
}

resource "google_cloud_run_service_iam_member" "cloud_run_invoker" {
  for_each = toset(var.data_providers)

  project  = var.gcp_project_id
  location = google_cloudfunctions2_function.data_gathering_function[each.key].location
  service  = google_cloudfunctions2_function.data_gathering_function[each.key].name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.cloud_function_sa.email}"
}

resource "google_cloud_scheduler_job" "data_gathering_scheduler" {
  for_each = toset(var.data_providers)

  project     = var.gcp_project_id
  name        = "${each.value}-data-gathering-scheduler"
  description = "Data gathering scheduler for ${each.value}"
  schedule    = "*/5 * * * *"
  time_zone   = "UTC"
  region      = var.gcp_region

  http_target {
    uri         = google_cloudfunctions2_function.data_gathering_function[each.key].service_config[0].uri
    http_method = "POST"
    oidc_token {
      audience              = "${google_cloudfunctions2_function.data_gathering_function[each.key].service_config[0].uri}/"
      service_account_email = google_service_account.cloud_function_sa.email
    }
  }
}
