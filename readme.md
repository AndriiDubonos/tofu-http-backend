# How to run
1. `docker compose up`
2. `docker compose run terraform_usage init`
3. `docker compose run terraform_usage apply -auto-approve`
4. `docker compose run terraform_data_source init`
5. `docker compose run terraform_data_source apply -auto-approve`

# Chalenges:
- I was struggling to come up with a good name for the entity that is managed by the API. I stopped on the `state` but I feel that there is actually two entities. Main one (like "config" or "infrastructure") for which we could save multiple states. But I decided to keep a single name because API itself is using name `state` for both - e.g. locking of **states** (even though we are locking "config"). 