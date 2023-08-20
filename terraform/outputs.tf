output "deployed_service_url" {
  value = google_cloud_run_service.default.status[0].url
  description = "The URL of the deployed service in Cloud Run"
}
