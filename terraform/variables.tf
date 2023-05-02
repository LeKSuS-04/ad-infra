variable "yandex_cloud_folder_id" {
  description = "Folder that will contain created resources"
  type        = string
  nullable    = false
}

variable "yandex_cloud_zone" {
  description = "Zone that will contain created resources"
  type        = string
  nullable    = false
  default     = "ru-central1-a"
}

variable "yandex_cloud_iam_token" {
  description = "IAM token of admin account"
  type        = string
  nullable    = false
}
