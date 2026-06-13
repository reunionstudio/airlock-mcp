from __future__ import annotations

import json
from typing import Any

from .specs import spec_name


def render_admin_sql(spec_config: dict[str, Any], *, app_name: str, operation: str) -> str:
    body = json.dumps(spec_config, indent=2)
    current_spec = spec_name(spec_config)
    if operation == "alter":
        escaped = current_spec.replace("'", "''")
        return f"CALL {app_name}.admin.alter_spec('{escaped}', PARSE_JSON($${body}$$), TRUE);"
    return f"CALL {app_name}.admin.create_spec(PARSE_JSON($${body}$$), TRUE);"
