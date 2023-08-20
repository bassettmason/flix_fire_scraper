variable "gcp_credentials_file" {
  description = "Path to the GCP credentials JSON file"
  default     = "./credentials.json"
}

variable "project_id" {
  description = "GCP project ID"
  default     = "media-djinn"
}

variable "region" {
  description = "The region to deploy resources in"
  default     = "us-west1"
}

variable "service_name" {
  description = "The name of the Cloud Run service"
  default     = "flix-fire-scraper-api"
}

variable "image_name" {
  description = "Name of the Docker image in GAR"
  default     = "flix-fire-scraper-image:latest" 
}

variable "repository_id" {
  description = "ID of the Artifact Registry repository"
  default     = "media-djinn-registry" 
}
