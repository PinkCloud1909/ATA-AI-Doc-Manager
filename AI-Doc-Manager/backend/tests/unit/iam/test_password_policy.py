import pytest

from app.core.exceptions import ValidationError
from app.modules.iam.domain.password_policy import (
    password_policy_errors,
    validate_password_policy,
)


@pytest.mark.parametrize(
    "password",
    [
        "StrongPass1!",
        "Another-Secure2",
        "VietNam@2026",
    ],
)
def test_accepts_passwords_that_satisfy_every_rule(password: str) -> None:
    assert password_policy_errors(password) == []
    validate_password_policy(password)


@pytest.mark.parametrize(
    ("password", "expected_rule"),
    [
        ("Short1!", "at least 8 characters"),
        ("lowercase1!", "one uppercase letter"),
        ("UPPERCASE1!", "one lowercase letter"),
        ("NoNumber!", "one number"),
        ("NoSpecial1", "one special character"),
        ("Has Space1!", "no whitespace"),
    ],
)
def test_reports_each_password_policy_violation(
    password: str,
    expected_rule: str,
) -> None:
    assert expected_rule in password_policy_errors(password)
    with pytest.raises(ValidationError, match=expected_rule):
        validate_password_policy(password)
