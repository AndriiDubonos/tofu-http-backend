# Please replace the address with your own REST API endpoint.
terraform {
  backend "http" {
    address = "http://tofu_http_backend:8000/states/scalr"
    lock_address = "http://tofu_http_backend:8000/states/scalr/lock"
    unlock_address = "http://tofu_http_backend:8000/states/scalr/unlock"
    lock_method = "POST"
    unlock_method = "POST"
    # additional headers can be set here or options
  }
}

resource "null_resource" "example" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "echo Hello from the custom HTTP backend for OpenTofu!"
  }
}