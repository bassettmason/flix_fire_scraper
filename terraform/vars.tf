variable "gcp_credentials_file" {
  description = "Path to the GCP credentials JSON file"
  default     = "./credentials.json"  # you can adjust this path
}

variable "project_id" {
  description = "The ID of the project in GCP"
}

variable "region" {
  description = "The region to deploy resources in"
  default     = "us-central1"  # default to US central
}

variable "service_name" {
  description = "The name of the Cloud Run service"
  default     = "my-fastapi-service"
}

variable "image_name" {
  description = "Name of the Docker image in GAR"
  default     = "my-fastapi-image:latest"
}

variable "repository_id" {
  description = "ID of the Artifact Registry repository"
  default     = "my-repo-name"  # Replace with your actual repository name or remove the default if you want to provide it dynamically
}
