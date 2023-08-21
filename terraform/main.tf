provider "google" {
  credentials = file(var.gcp_credentials_file)
  project     = "media-djinn"
  region      = "us-west1"
}
# below creates a artifact registry repo dont need it because its already made
# resource "google_artifact_registry_repository" "default" {
#   location      = "us-west1"
#   repository_id = "media-djinn-registry"
#   format        = "DOCKER"

#   lifecycle {
#     prevent_destroy = true
#     ignore_changes  = [repository_id]
#   }
# }


# resource "google_cloud_run_service" "default" {
#   name     = var.service_name
#   location = "us-west1"

#   template {
#     spec {
#       containers {
#         image = "us-west1-docker.pkg.dev/media-djinn/media-djinn-registry/${var.image_name}"
#       }
#     }
#   }

#   traffic {
#     percent         = 100
#     latest_revision = true
#   }
# }

# output "service_url" {
#   value = google_cloud_run_service.default.status[0].url
# }
