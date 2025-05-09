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

data "terraform_remote_state" "foo" {
  backend = "http"
  config = {
    address = "http://tofu_http_backend:8000/states/scalr"
  }
}

resource "null_resource" "example" {
    triggers = {
        always_run = timestamp()
    }
    provisioner "local-exec" {
        command = "echo Hello from the custom HTTP backend for OpenTofu! ${jsonencode(data.terraform_remote_state.foo.outputs)}"
    }
}
