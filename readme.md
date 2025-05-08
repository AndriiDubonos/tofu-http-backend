# How to run
1. `docker compose up`
2. `docker compose run terraform_usage init`
3. `docker compose run terraform_usage apply -auto-approve`
4. `docker compose run terraform_data_source init`
5. `docker compose run terraform_data_source apply -auto-approve`

# How to run tests

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