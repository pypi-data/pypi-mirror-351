from pathlib import Path

import pytest

from zgw_consumers_oas import read_schema

TESTS_DIR = Path(__file__).parent


@pytest.mark.parametrize("schema", ["dummy", "schema"])
def test_exception_raised_not_found(settings, schema):
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = []

    with pytest.raises(IOError):
        read_schema(schema)


@pytest.mark.parametrize("name", ["dummy", "schema"])
def test_read_schema_from_dirs(settings, name, schema_cache):
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [
        TESTS_DIR / "schemas",
        TESTS_DIR / "schemas" / "nested",
    ]

    schema = read_schema(name)

    assert f"name: {name}".encode("utf-8") in schema
