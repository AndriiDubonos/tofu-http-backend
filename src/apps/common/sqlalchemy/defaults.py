from sqlalchemy import text

server_default_uuid4 = text('gen_random_uuid()')
server_default_now = text("now() at time zone 'utc'")
