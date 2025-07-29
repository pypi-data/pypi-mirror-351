import re
from datetime import datetime
from pathlib import Path

from zgw_consumers_oas import generate_oas_component

TESTS_DIR = Path(__file__).parent

DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def test_component_generation(settings):
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [TESTS_DIR / "schemas"]

    component = generate_oas_component("drc", "schemas/EnkelvoudigInformatieObject")

    assert component["url"].startswith("http")
    assert isinstance(component["identificatie"], str)
    assert DATE_RE.match(component["creatiedatum"])
    assert component["vertrouwelijkheidaanduiding"] in [
        "openbaar",
        "beperkt_openbaar",
        "intern",
        "zaakvertrouwelijk",
        "vertrouwelijk",
        "confidentieel",
        "geheim",
        "zeer_geheim",
    ]
    assert len(component["taal"]) == 3

    begin_registratie = datetime.fromisoformat(component["beginRegistratie"])
    assert isinstance(begin_registratie, datetime)
    assert component["ondertekening"] is None
    assert isinstance(component["locked"], bool)
