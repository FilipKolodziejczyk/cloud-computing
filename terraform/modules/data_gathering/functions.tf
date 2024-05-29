terraform {
  required_providers {
    time = {
      source = "hashicorp/time"
    }
  }
}

resource "google_service_account" "cloud_function_sa" {
  project      = var.gcp_project_id
  account_id   = "cloud-function-sa"
  display_name = "Cloud Function Service Account"
}

resource "google_project_iam_member" "cloud_function_pubsub_publisher" {
  project = var.gcp_project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.cloud_function_sa.email}"
}

resource "google_storage_bucket" "cloud_function_source_bucket" {
  project                     = var.gcp_project_id
  name                        = "${var.gcp_project_id}-cloud-function-source-bucket"
  location                    = var.gcp_region
  uniform_bucket_level_access = true
}

locals {
  current_date = provider::time::rfc3339_parse(timestamp()).unix
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
      zip -r "${each.value}-${local.current_date}.zip" .
    EOH
  }
}

resource "google_storage_bucket_object" "cloud_function_source" {
  depends_on = [null_resource.zip_sources]

  for_each = toset(var.data_providers)

  name   = "${each.value}.zip"
  bucket = google_storage_bucket.cloud_function_source_bucket.name
  source = "${path.root}/artifacts/${each.value}-${local.current_date}.zip"
}

resource "google_pubsub_topic" "data_gathering_function_trigger" {
  for_each = toset(var.data_providers)

  project = var.gcp_project_id
  name    = "${lower(each.value)}-data-gathering-function-trigger"
}


resource "google_cloudfunctions2_function" "data_gathering_function" {
  for_each = toset(var.data_providers)

  lifecycle {
    replace_triggered_by = [
      google_storage_bucket_object.cloud_function_source[each.key]
    ]
  }

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
      GCP_PROJECT_ID        = var.gcp_project_id
      PUBSUB_TOPIC_ID       = var.pubsub_real_time_topic[each.key]
      PUBSUB_BATCH_TOPIC_ID = var.pubsub_batch_topic[each.key]
    }
  }

  event_trigger {
    trigger_region = var.gcp_region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.data_gathering_function_trigger[each.key].id
    retry_policy   = "RETRY_POLICY_RETRY"
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
  schedule    = "*/30 * * * *"
  time_zone   = "UTC"
  region      = var.gcp_region

  pubsub_target {
    topic_name = google_pubsub_topic.data_gathering_function_trigger[each.key].id
    data       = base64encode("Invoke ${each.value} data gathering function")
  }
}
