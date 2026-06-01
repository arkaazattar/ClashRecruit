"""Request validation helpers shared by Flask routes."""

import re
from typing import Any

from flask import Request

TAG_PATTERN = re.compile(r"^[A-Z0-9]+$")
CLASH_WAR_FREQUENCIES = {
    "always",
    "moreThanOncePerWeek",
    "oncePerWeek",
    "lessThanOncePerWeek",
    "never",
}


class RequestValidationError(ValueError):
    """Raised when client supplied request data is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def get_json_object(request: Request) -> dict[str, Any]:
    """Return the request JSON body as an object."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise RequestValidationError("Request body must be a JSON object.")
    return payload


def query_int(
    request: Request,
    field_name: str,
    *,
    default: int,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Return a validated integer query parameter."""
    value = request.args.get(field_name)
    if value is None:
        return default

    parsed = _parse_int(value, field_name)
    _validate_int_bounds(parsed, field_name, min_value, max_value)
    return parsed


def query_bool(
    request: Request,
    field_name: str,
    *,
    default: bool = False,
) -> bool:
    """Return a validated boolean query parameter."""
    value = request.args.get(field_name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true"}:
        return True
    if normalized in {"0", "false"}:
        return False
    raise RequestValidationError(f"{field_name} must be true or false.")


def ensure_object(value: Any, field_name: str) -> dict[str, Any]:
    """Return a dict value or raise a validation error for bad shape."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise RequestValidationError(f"{field_name} must be an object.")
    return value


def ensure_allowed_fields(
    payload: dict[str, Any],
    allowed_fields: set[str],
    object_name: str,
) -> None:
    """Raise when a request object contains unsupported fields."""
    unknown_fields = sorted(set(payload) - allowed_fields)
    if unknown_fields:
        raise RequestValidationError(
            f"Unsupported {object_name} field: {unknown_fields[0]}."
        )


def ensure_exactly_one_field(
    payload: dict[str, Any],
    field_names: set[str],
    object_name: str,
) -> str:
    """Return the single present field from a one-of request contract."""
    present_fields = sorted(field_names & set(payload))
    if len(present_fields) != 1:
        expected = " or ".join(sorted(field_names))
        raise RequestValidationError(
            f"{object_name} must include exactly one of {expected}."
        )
    return present_fields[0]


def optional_string(
    payload: dict[str, Any],
    field_name: str,
    *,
    max_length: int | None = None,
) -> str | None:
    """Return an optional trimmed string field."""
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise RequestValidationError(f"{field_name} must be a string.")

    normalized = value.strip()
    if max_length is not None and len(normalized) > max_length:
        raise RequestValidationError(
            f"{field_name} must be {max_length} characters or fewer."
        )
    return normalized


def required_string(
    payload: dict[str, Any],
    field_name: str,
    *,
    max_length: int | None = None,
) -> str:
    """Return a required trimmed string field."""
    value = optional_string(payload, field_name, max_length=max_length)
    if not value:
        raise RequestValidationError(f"{field_name} is required.")
    return value


def optional_bool(payload: dict[str, Any], field_name: str) -> bool | None:
    """Return an optional boolean field."""
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise RequestValidationError(f"{field_name} must be a boolean.")
    return value


def optional_enum(
    payload: dict[str, Any],
    field_name: str,
    allowed_values: set[str],
) -> str | None:
    """Return an optional string enum field."""
    value = optional_string(payload, field_name, max_length=40)
    if not value:
        return None
    if value not in allowed_values:
        raise RequestValidationError(f"{field_name} is invalid.")
    return value


def optional_int(
    payload: dict[str, Any],
    field_name: str,
    *,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int | None:
    """Return an optional integer, accepting integer-looking strings."""
    value = payload.get(field_name)
    if value is None:
        return None

    parsed = _parse_int(value, field_name)
    _validate_int_bounds(parsed, field_name, min_value, max_value)
    return parsed


def required_int(
    payload: dict[str, Any],
    field_name: str,
    *,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Return a required integer, accepting integer-looking strings."""
    value = payload.get(field_name)
    if value is None:
        raise RequestValidationError(f"{field_name} is required.")

    parsed = _parse_int(value, field_name)
    _validate_int_bounds(parsed, field_name, min_value, max_value)
    return parsed


def normalize_tag(value: Any, field_name: str) -> str:
    """Normalize a Clash-style tag used as an application identity key."""
    if not isinstance(value, str):
        raise RequestValidationError(f"{field_name} must be a string.")

    normalized = value.strip().lstrip("#").upper()
    if not normalized:
        raise RequestValidationError(f"{field_name} is required.")
    if not TAG_PATTERN.fullmatch(normalized):
        raise RequestValidationError(
            f"{field_name} must contain only letters and numbers."
        )
    return normalized


def _parse_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool):
        raise RequestValidationError(f"{field_name} must be an integer.")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped and stripped.isdecimal():
            return int(stripped)
    raise RequestValidationError(f"{field_name} must be an integer.")


def _validate_int_bounds(
    value: int,
    field_name: str,
    min_value: int | None,
    max_value: int | None,
) -> None:
    if min_value is not None and value < min_value:
        raise RequestValidationError(
            f"{field_name} must be at least {min_value}."
        )
    if max_value is not None and value > max_value:
        raise RequestValidationError(
            f"{field_name} must be at most {max_value}."
        )
