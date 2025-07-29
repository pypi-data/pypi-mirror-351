import os
import threading

from .settings import get_setting

_cache: dict[str, bytes] = {}
lock = threading.Lock()


def read_schema(service: str, extension=".yaml") -> bytes:
    schema_dirs = get_setting("ZGW_CONSUMERS_TEST_SCHEMA_DIRS")

    with lock:
        if service not in _cache:
            file_name = f"{service}{extension}"
            for directory in schema_dirs:
                filepath = os.path.join(directory, file_name)
                if os.path.exists(filepath):
                    break
            else:
                _directories = [str(path) for path in schema_dirs]
                raise IOError(
                    f"File '{file_name}' not found, searched directories: {', '.join(_directories)}. "
                    "Consider adding the containing directory to the ZGW_CONSUMERS_TEST_SCHEMA_DIRS setting."
                )

            with open(filepath, "rb") as api_spec:
                _cache[service] = api_spec.read()

        return _cache[service]
