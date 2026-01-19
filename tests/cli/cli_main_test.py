import sys

import pytest

from click.exceptions import Exit
from pytest_mock import MockerFixture

from svs_core.__main__ import global_options, version_callback


@pytest.mark.cli
class TestMainCLI:
    @pytest.fixture(autouse=True)
    def reset_context(self):
        """Reset context before each test."""
        from svs_core.cli.state import current_user, verbose_mode

        current_user.set(None)
        verbose_mode.set(False)

    def test_version_callback_prints_version(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that version callback prints version and exits."""
        with pytest.raises(Exit):
            version_callback(True)

        captured = capsys.readouterr()
        assert "SVS version:" in captured.out

    def test_version_callback_does_nothing_when_false(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that version callback doesn't exit when value is False."""
        version_callback(False)

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_global_options_sets_verbose_mode(self, mocker: MockerFixture) -> None:
        """Test that global_options sets verbose mode correctly."""
        from svs_core.cli.state import is_verbose

        mocker.patch("svs_core.__main__.add_verbose_handler")
        mocker.patch("svs_core.__main__.get_logger")

        global_options(version_flag=False, verbose=True, user_override=None)

        assert is_verbose() is True

    def test_global_options_does_not_set_verbose_mode_when_false(
        self, mocker: MockerFixture
    ) -> None:
        """Test that global_options doesn't set verbose mode when flag is
        False."""
        from svs_core.cli.state import is_verbose

        global_options(version_flag=False, verbose=False, user_override=None)

        assert is_verbose() is False

    def test_global_options_calls_add_verbose_handler_when_verbose(
        self, mocker: MockerFixture
    ) -> None:
        """Test that add_verbose_handler is called when verbose is True."""
        mock_add_verbose = mocker.patch("svs_core.__main__.add_verbose_handler")
        mock_logger = mocker.patch("svs_core.__main__.get_logger")

        global_options(version_flag=False, verbose=True, user_override=None)

        mock_add_verbose.assert_called_once()

    def test_global_options_does_not_call_add_verbose_handler_when_not_verbose(
        self, mocker: MockerFixture
    ) -> None:
        """Test that add_verbose_handler is not called when verbose is
        False."""
        mock_add_verbose = mocker.patch("svs_core.__main__.add_verbose_handler")

        global_options(version_flag=False, verbose=False, user_override=None)

        mock_add_verbose.assert_not_called()

    def test_global_options_logs_debug_when_verbose(
        self, mocker: MockerFixture
    ) -> None:
        """Test that debug message is logged when verbose is True."""
        mock_add_verbose = mocker.patch("svs_core.__main__.add_verbose_handler")
        mock_logger_instance = mocker.MagicMock()
        mock_get_logger = mocker.patch(
            "svs_core.__main__.get_logger", return_value=mock_logger_instance
        )

        global_options(version_flag=False, verbose=True, user_override=None)

        mock_get_logger.assert_called()
        mock_logger_instance.debug.assert_called_once()

    def test_global_options_does_not_log_debug_when_not_verbose(
        self, mocker: MockerFixture
    ) -> None:
        """Test that debug message is not logged when verbose is False."""
        mock_logger_instance = mocker.MagicMock()
        mock_get_logger = mocker.patch(
            "svs_core.__main__.get_logger", return_value=mock_logger_instance
        )

        global_options(version_flag=False, verbose=False, user_override=None)

        mock_logger_instance.debug.assert_not_called()

    def test_global_options_with_both_flags(self, mocker: MockerFixture) -> None:
        """Test global_options behavior when both version and verbose are
        passed."""
        from svs_core.cli.state import is_verbose

        mock_add_verbose = mocker.patch("svs_core.__main__.add_verbose_handler")
        mocker.patch("svs_core.__main__.get_logger")

        global_options(version_flag=False, verbose=True, user_override=None)

        assert is_verbose() is True
        mock_add_verbose.assert_called_once()

    def test_cli_first_user_setup_success_with_provided_credentials(
        self, mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test cli_first_user_setup successfully creates user with provided
        credentials."""
        from svs_core.__main__ import cli_first_user_setup

        mock_user_create = mocker.patch("svs_core.users.user.User.create")

        cli_first_user_setup("testuser", "testpass")

        mock_user_create.assert_called_once_with("testuser", "testpass", True)

    def test_cli_first_user_setup_failure_with_provided_credentials(
        self, mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test cli_first_user_setup handles creation failure with provided
        credentials."""
        from svs_core.__main__ import cli_first_user_setup

        mock_user_create = mocker.patch(
            "svs_core.users.user.User.create",
            side_effect=Exception("User already exists"),
        )

        cli_first_user_setup("testuser", "testpass")

        captured = capsys.readouterr()
        assert "Failed to create user with provided credentials" in captured.out

    def test_cli_first_user_setup_prompts_for_credentials_when_not_provided(
        self, mocker: MockerFixture
    ) -> None:
        """Test cli_first_user_setup prompts for username and password when not
        provided."""
        from svs_core.__main__ import cli_first_user_setup

        mock_user_create = mocker.patch("svs_core.users.user.User.create")
        mock_input = mocker.patch("builtins.input", return_value="prompted_user")
        mock_getpass = mocker.patch(
            "svs_core.__main__.getpass", return_value="prompted_pass"
        )

        cli_first_user_setup()

        mock_input.assert_called()
        mock_getpass.assert_called()
        mock_user_create.assert_called_once_with("prompted_user", "prompted_pass", True)

    def test_cli_first_user_setup_retries_on_failure_without_credentials(
        self, mocker: MockerFixture
    ) -> None:
        """Test cli_first_user_setup retries when creation fails without
        provided credentials."""
        from svs_core.__main__ import cli_first_user_setup

        mock_user_create = mocker.patch(
            "svs_core.users.user.User.create",
            # First call fails, second succeeds
            side_effect=[Exception("Error"), None],
        )
        mock_input = mocker.patch(
            "builtins.input",
            side_effect=["user1", "user2"],
        )
        mock_getpass = mocker.patch(
            "svs_core.__main__.getpass",
            side_effect=["pass1", "pass2"],
        )

        cli_first_user_setup()

        # Should be called twice (once fails, once succeeds)
        assert mock_user_create.call_count == 2

    def test_main_exits_when_sudo_user_env_not_set(
        self, mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that main exits when SUDO_USER environment variable is not
        set."""
        from svs_core.__main__ import main
        from svs_core.users.user import User

        # Mock dependencies
        mock_system_user = mocker.patch(
            "svs_core.users.system.SystemUserManager.get_system_username",
            return_value="testuser",
        )
        mock_user_filter = mocker.MagicMock()
        mock_user_filter.first.return_value = mocker.MagicMock(
            name="testuser", is_admin=lambda: False
        )
        mocker.patch.object(User.objects, "filter", return_value=mock_user_filter)
        # Ensure SUDO_USER is not set
        mocker.patch.dict("os.environ", {}, clear=False)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "must be run with sudo privileges" in captured.out

    def test_main_continues_when_sudo_user_env_is_set(
        self, mocker: MockerFixture
    ) -> None:
        """Test that main continues when SUDO_USER environment variable is
        set."""
        from svs_core.__main__ import main
        from svs_core.users.user import User

        # Mock dependencies
        mock_system_user = mocker.patch(
            "svs_core.users.system.SystemUserManager.get_system_username",
            return_value="testuser",
        )
        mock_user = mocker.MagicMock()
        mock_user.name = "testuser"
        mock_user.is_admin.return_value = False
        mock_user_filter = mocker.MagicMock()
        mock_user_filter.first.return_value = mock_user
        mocker.patch.object(User.objects, "filter", return_value=mock_user_filter)
        mocker.patch.dict("os.environ", {"SUDO_USER": "testuser"}, clear=False)
        mock_app = mocker.patch("svs_core.__main__.app")

        main()

        mock_app.assert_called_once()

    def test_main_exits_when_user_not_found(
        self, mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that main exits when user is not found in database."""
        from svs_core.__main__ import main
        from svs_core.users.user import User

        # Mock dependencies
        mock_system_user = mocker.patch(
            "svs_core.users.system.SystemUserManager.get_system_username",
            return_value="nonexistent",
        )
        mock_user_filter = mocker.MagicMock()
        mock_user_filter.first.return_value = None
        mocker.patch.object(User.objects, "filter", return_value=mock_user_filter)
        mocker.patch.dict("os.environ", {"SUDO_USER": "testuser"}, clear=False)
        mock_logger = mocker.MagicMock()
        mocker.patch("svs_core.__main__.get_logger", return_value=mock_logger)

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "no matching SVS user was" in captured.out
        mock_logger.warning.assert_called()

    def test_main_sets_current_user_when_valid(self, mocker: MockerFixture) -> None:
        """Test that main sets the current user when all checks pass."""
        from svs_core.__main__ import main
        from svs_core.users.user import User

        # Mock dependencies
        mock_system_user = mocker.patch(
            "svs_core.users.system.SystemUserManager.get_system_username",
            return_value="testuser",
        )
        mock_user = mocker.MagicMock()
        mock_user.name = "testuser"
        mock_user.is_admin.return_value = True
        mock_user_filter = mocker.MagicMock()
        mock_user_filter.first.return_value = mock_user
        mocker.patch.object(User.objects, "filter", return_value=mock_user_filter)
        mocker.patch.dict("os.environ", {"SUDO_USER": "testuser"}, clear=False)
        mock_set_current_user = mocker.patch("svs_core.__main__.set_current_user")
        mock_get_logger = mocker.MagicMock()
        mocker.patch("svs_core.__main__.get_logger", return_value=mock_get_logger)
        mock_app = mocker.patch("svs_core.__main__.app")

        main()

        mock_set_current_user.assert_called_once_with("testuser", True)
        mock_app.assert_called_once()
