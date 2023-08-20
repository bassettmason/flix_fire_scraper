provider "google" {
  credentials = file(var.gcp_credentials_file)
  project     = "media-djinn"
  region      = "us-west1"
}

resource "google_artifact_registry_repository" "default" {
  location      = "us-west1"
  repository_id = "media-djinn-registry"
  format        = "DOCKER"
}

  # template {
  #   spec {
  #     service_account_name = "ci-cd-service-account@media-djinn.iam.gserviceaccount.com"

  #     containers {
  #       image = "us-west1-docker.pkg.dev/media-djinn/media-djinn-registry/${var.image_name}"
  #     }
  #   }
  # }




