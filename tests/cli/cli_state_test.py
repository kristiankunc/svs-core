import sys

import pytest

from pytest_mock import MockerFixture

from svs_core.cli.state import (
    current_user,
    get_current_username,
    is_current_user_admin,
    is_verbose,
    reject_if_not_admin,
    set_current_user,
    set_verbose_mode,
    verbose_mode,
)


@pytest.mark.cli
class TestState:
    @pytest.fixture(autouse=True)
    def reset_context(self):
        """Reset context variables before each test."""
        current_user.set(None)
        verbose_mode.set(False)

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

    def test_set_verbose_mode_true(self) -> None:
        set_verbose_mode(True)
        assert is_verbose() is True

    def test_set_verbose_mode_false(self) -> None:
        set_verbose_mode(True)
        set_verbose_mode(False)
        assert is_verbose() is False

    def test_is_verbose_default_false(self) -> None:
        assert is_verbose() is False

    def test_verbose_mode_independent_of_user(self) -> None:
        """Verify that verbose mode is independent of user state."""
        set_current_user("user1", True)
        set_verbose_mode(True)

        assert get_current_username() == "user1"
        assert is_verbose() is True

        set_current_user("user2", False)
        assert get_current_username() == "user2"
        assert is_verbose() is True  # Verbose mode should remain True

    def test_multiple_verbose_toggles(self) -> None:
        """Test toggling verbose mode multiple times."""
        assert is_verbose() is False

        set_verbose_mode(True)
        assert is_verbose() is True

        set_verbose_mode(False)
        assert is_verbose() is False

        set_verbose_mode(True)
        assert is_verbose() is True
