import sys

import pytest

from pytest_mock import MockerFixture

from svs_core.cli.state import (
    current_user,
    get_current_username,
    is_current_user_admin,
    reject_if_not_admin,
    set_current_user,
)


@pytest.mark.cli
class TestState:
    def test_set_current_user(self) -> None:
        set_current_user("john_doe", True)
        assert get_current_username() == "john_doe"
        assert is_current_user_admin() is True

    def test_get_current_username_when_set(self) -> None:
        set_current_user("alice", False)
        assert get_current_username() == "alice"

    def test_get_current_username_when_not_set(self) -> None:
        current_user.set(None)
        assert get_current_username() is None

    def test_is_current_user_admin_true(self) -> None:
        set_current_user("admin_user", True)
        assert is_current_user_admin() is True

    def test_is_current_user_admin_false(self) -> None:
        set_current_user("regular_user", False)
        assert is_current_user_admin() is False

    def test_is_current_user_admin_when_not_set(self) -> None:
        current_user.set(None)
        assert is_current_user_admin() is False

    def test_reject_if_not_admin_with_admin(self, mocker: MockerFixture) -> None:
        set_current_user("admin_user", True)
        # Should not raise or exit
        reject_if_not_admin()

    def test_reject_if_not_admin_with_non_admin(self, mocker: MockerFixture) -> None:
        set_current_user("regular_user", False)
        mock_exit = mocker.patch("sys.exit")
        mock_print = mocker.patch("builtins.print")

        reject_if_not_admin()

        mock_print.assert_called_once()
        mock_exit.assert_called_once_with(1)

    def test_reject_if_not_admin_when_user_not_set(self, mocker: MockerFixture) -> None:
        current_user.set(None)
        mock_exit = mocker.patch("sys.exit")
        mock_print = mocker.patch("builtins.print")

        reject_if_not_admin()

        mock_print.assert_called_once()
        mock_exit.assert_called_once_with(1)
