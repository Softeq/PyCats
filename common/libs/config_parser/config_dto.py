from dataclasses import dataclass


@dataclass
class APIValidationDTO:
    check_status_code: bool
    check_headers: bool
    check_body: bool
    fail_if_field_is_missing: bool