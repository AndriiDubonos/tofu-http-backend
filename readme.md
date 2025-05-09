# Overview

This project implements a custom HTTP backend for OpenTofu/Terraform state management. It provides a REST API that allows storing, retrieving, locking, and unlocking Terraform state files.

## Key Features

- **State Storage**: Stores Terraform state files in MinIO
- **State Locking**: Prevents concurrent modifications to state files through a locking mechanism
- **State Versioning**: Maintains a history of state versions for auditing and rollback capabilities
- **Authentication**: Basic HTTP authentication for securing state access
- **PostgreSQL Backend**: Uses PostgreSQL for storing metadata about states and locks

## Architecture

Application is built with usage of Ports and Adapters architecture.
Business domain split into subdomains (while only single domain in this project exists).
Business logic is implemented in the domain layer (`domain/`).
Data access (postgres, media storage) is implemented in the infrastructure layer (`data_access/`).
Available actions for the system are implemented in the use cases layer (`use_cases/`).
State is passed and managed by the Unit of Work Pattern.

# How to run
1. `docker compose up`
2. `docker compose run terraform_usage init`
3. `docker compose run terraform_usage apply -auto-approve`
4. `docker compose run terraform_data_source init`
5. `docker compose run terraform_data_source apply -auto-approve`

# How to run tests
1. `docker compose up`
2. `docker exec -it tofu_http_backend sh`
3. `pytest`

### Example of requests
```
b''
INFO:     172.25.0.2:34466 - "GET /states/scalr HTTP/1.1" 404 Not Found
b'{"ID":"302dec55-3b0b-3ffa-a336-f9f4317e4dad","Operation":"OperationTypeApply","Info":"","Who":"root@2be4e4840b40","Version":"1.9.1","Created":"2025-05-07T16:24:13.133931087Z","Path":""}'
INFO:     172.25.0.2:45402 - "POST /states/scalr/lock HTTP/1.1" 200 OK
b''
INFO:     172.25.0.2:45406 - "GET /states/scalr HTTP/1.1" 404 Not Found
b''
INFO:     172.25.0.2:45418 - "GET /states/scalr HTTP/1.1" 404 Not Found
b'{"version":4,"terraform_version":"1.9.1","serial":1,"lineage":"2fbf9278-4e7b-1228-9f69-d27ce621d75b","outputs":{},"resources":[{"mode":"managed","type":"null_resource","name":"example","provider":"provider[\\"registry.opentofu.org/hashicorp/null\\"]","instances":[{"schema_version":0,"attributes":{"id":"588398148598976215","triggers":{"always_run":"2025-05-07T16:24:13Z"}},"sensitive_attributes":[]}]}],"check_results":null}\n'
INFO:     172.25.0.2:45422 - "POST /states/scalr?ID=302dec55-3b0b-3ffa-a336-f9f4317e4dad HTTP/1.1" 200 OK
b'{"ID":"302dec55-3b0b-3ffa-a336-f9f4317e4dad","Operation":"OperationTypeApply","Info":"","Who":"root@2be4e4840b40","Version":"1.9.1","Created":"2025-05-07T16:24:13.133931087Z","Path":""}'
INFO:     172.25.0.2:45428 - "POST /states/scalr/unlock HTTP/1.1" 200 OK

```