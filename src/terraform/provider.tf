terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
  required_version = ">= 0.13"
}

provider "yandex" {
  folder_id = var.yandex_cloud.folder_id
  zone      = var.yandex_cloud.zone
  token     = var.yandex_cloud.iam_token
}
