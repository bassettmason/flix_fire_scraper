provider "google" {
  credentials = file(var.gcp_credentials_file)
  project     = "media-djinn"
  region      = "us-west1"
}

resource "google_artifact_registry_repository" "default" {
  location      = "us-west1"
  repository_id = "media-djinn"
  format        = "DOCKER"
}

resource "google_cloud_run_service" "default" {
  name     = var.service_name
  location = "us-west1"

  template {
    spec {
      containers {
        image = "us-west1-docker.pkg.dev/media-djinn/media-djinn-registry/${var.image_name}"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

output "service_url" {
  value = google_cloud_run_service.default.status[0].url
}
