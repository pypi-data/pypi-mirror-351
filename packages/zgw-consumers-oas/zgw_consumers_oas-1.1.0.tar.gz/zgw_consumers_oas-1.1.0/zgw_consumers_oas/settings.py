# Deliberately supports the (deprecated) settings from zgw-consumers
from django.conf import settings

ZGW_CONSUMERS_TEST_SCHEMA_DIRS = []


def get_setting(name: str):
    default = globals()[name]
    return getattr(settings, name, default)
