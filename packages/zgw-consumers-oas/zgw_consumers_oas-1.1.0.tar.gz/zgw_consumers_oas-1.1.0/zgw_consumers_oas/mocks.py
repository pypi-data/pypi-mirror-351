from requests_mock import Mocker

from .schema_loading import read_schema


def mock_service_oas_get(m: Mocker, url: str, service: str, oas_url: str = "") -> None:
    if not oas_url:
        oas_url = f"{url}schema/openapi.yaml?v=3"
    content = read_schema(service)
    m.get(oas_url, content=content)
