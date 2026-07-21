"""Password policy shared by all IAM password-writing flows."""

import re

from app.core.exceptions import ValidationError


PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


def password_policy_errors(password: str) -> list[str]:
    """Return all password policy violations in a user-friendly order."""
    errors: list[str] = []
    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f"at least {PASSWORD_MIN_LENGTH} characters")
    if len(password) > PASSWORD_MAX_LENGTH:
        errors.append(f"at most {PASSWORD_MAX_LENGTH} characters")
    if not re.search(r"[A-Z]", password):
        errors.append("one uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("one lowercase letter")
    if not re.search(r"\d", password):
        errors.append("one number")
    if not re.search(r"[^A-Za-z0-9\s]", password):
        errors.append("one special character")
    if any(character.isspace() for character in password):
        errors.append("no whitespace")
    return errors


def validate_password_policy(password: str) -> None:
    """Raise the application validation error when *password* is too weak."""
    errors = password_policy_errors(password)
    if errors:
        raise ValidationError("Password must contain " + ", ".join(errors) + ".")
