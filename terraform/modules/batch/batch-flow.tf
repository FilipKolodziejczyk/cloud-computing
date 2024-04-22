resource "google_pubsub_topic" "data_provider_topic_batch" {
  for_each = toset(var.data_providers)

  project = var.gcp_project_id
  name    = "${each.value}-batch-topic"
}

resource "google_pubsub_subscription" "data_provider_subscription_batch" {
  for_each = toset(var.data_providers)

  project = var.gcp_project_id
  name    = "${each.value}-batch-subscription"
  topic   = google_pubsub_topic.data_provider_topic_batch[each.key].name
}

resource "google_storage_bucket" "dataflow_temp_bucket" {
  project  = var.gcp_project_id
  name     = "${var.gcp_project_id}-dataflow-batch-temp-bucket"
  location = var.gcp_region
}

# Dataflow pipeline (must be set up manually for now, since flex template must be created piror to running the job
# resource "google_dataflow_flex_template_job" "batch_dataflow" {
#   name     = "${each.value}-batch-dataflow-${timestamp()}"
#   project  = var.project
#   region   = var.location
#   template_gcs_path = "gs://${google_storage_bucket.workflow_repo.name}/batch-dataflow-template"
#   temp_gcs_location = google_storage_bucket.dataflow_temp_bucket.url
#   on_delete = "cancel"
#   parameters = {
#     input_topic = google_pubsub_topic.data_provider_topic_batch[each.key].name
#     output_table = google_bigtable_table.bigtable_tables[each.key].name
#   }
# }

output "data_provider_topic_batch" {
  value = {
    for provider in var.data_providers : provider => google_pubsub_topic.data_provider_topic_batch[provider].name
  }
}

output "data_provider_subscription_batch" {
  value = {
    for provider in var.data_providers : provider => google_pubsub_subscription.data_provider_subscription_batch[provider].name
  }
}