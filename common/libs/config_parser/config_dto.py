from dataclasses import dataclass


@dataclass
class APIValidationDTO:
    check_status_code: bool
    check_headers: bool
    check_body: bool
    check_is_field_missing: bool
