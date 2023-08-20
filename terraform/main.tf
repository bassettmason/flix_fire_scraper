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

resource "google_cloud_run_service" "default" {
  name     = var.service_name
  location = "us-west1"

  template {
    spec {
      service_account_name = "ci-cd-service-account@media-djinn.iam.gserviceaccount.com"

      containers {
        image = "us-west1-docker.pkg.dev/media-djinn/media-djinn-registry/flix-fire-scraper-image:latest"
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
