from tofu_http_backend.app import create_app
from tofu_http_backend.settings.development import settings as development_settings

app = create_app(settings=development_settings)
