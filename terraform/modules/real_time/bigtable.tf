#resource "google_bigtable_instance" "real_time_bigtable" {
#  project             = var.gcp_project_id
#  name                = "real-time-bigtable"
#  deletion_protection = false
#
#  cluster {
#    cluster_id   = "default"
#    num_nodes    = 1
#    storage_type = "SSD"
#    zone         = var.gcp_zone
#  }
#}
#
#resource "google_bigtable_table" "bigtable_tables" {
#  for_each = toset(var.data_providers)
#
#  project       = var.gcp_project_id
#  name          = each.value
#  instance_name = google_bigtable_instance.real_time_bigtable.name
#
#  column_family {
#    family = "base"
#  }
#}
