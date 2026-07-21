from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from app.core.exceptions import ValidationError
from app.modules.iam.application.services import change_password, reset_user_password


def test_change_password_verifies_current_password_and_persists_hash() -> None:
    user_id = uuid4()
    user = SimpleNamespace(password_hash="old-hash", last_password_changed=None)
    session = Mock()

    with (
        patch(
            "app.modules.iam.application.services.get_user_by_id",
            return_value=user,
        ),
        patch(
            "app.modules.iam.application.services.verify_password",
            return_value=True,
        ) as verify,
        patch(
            "app.modules.iam.application.services.get_password_hash",
            return_value="new-hash",
        ),
    ):
        change_password(
            session,
            user_id=user_id,
            current_password="OldPass1!",
            new_password="NewPass2!",
        )

    verify.assert_called_once_with("OldPass1!", "old-hash")
    assert user.password_hash == "new-hash"
    assert user.last_password_changed is not None
    session.commit.assert_called_once()


def test_change_password_rejects_an_incorrect_current_password() -> None:
    user = SimpleNamespace(password_hash="old-hash", last_password_changed=None)
    with (
        patch(
            "app.modules.iam.application.services.get_user_by_id",
            return_value=user,
        ),
        patch(
            "app.modules.iam.application.services.verify_password",
            return_value=False,
        ),
        pytest.raises(ValidationError, match="Current password is incorrect"),
    ):
        change_password(
            Mock(),
            user_id=uuid4(),
            current_password="WrongPass1!",
            new_password="NewPass2!",
        )


def test_admin_reset_password_applies_policy_and_commits() -> None:
    user = SimpleNamespace(password_hash="old-hash", last_password_changed=None)
    session = Mock()
    with (
        patch(
            "app.modules.iam.application.services.get_user_by_id",
            return_value=user,
        ),
        patch(
            "app.modules.iam.application.services.get_password_hash",
            return_value="reset-hash",
        ),
    ):
        reset_user_password(
            session,
            user_id=uuid4(),
            new_password="ResetPass3!",
        )

    assert user.password_hash == "reset-hash"
    assert user.last_password_changed is not None
    session.commit.assert_called_once()
