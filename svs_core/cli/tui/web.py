import os
import sys

import django

from django.apps import apps as django_apps
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import (
    Button,
    Input,
    Label,
    Static,
)

from svs_core.cli.state import set_current_user
from svs_core.cli.tui.app import SVSTUIScreen

if not django_apps.ready:
    os.environ["DJANGO_SETTINGS_MODULE"] = "svs_core.db.settings"
    django.setup()

from svs_core.docker.service import Service
from svs_core.docker.template import Template
from svs_core.users.user import User


class LoginScreen(Screen[None]):
    """Login screen for SVS TUI."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the login screen."""
        with Container(id="login-container"):
            yield Label("SVS Login", id="login-title")
            yield Label("Username:", classes="input-label")
            yield Input(
                placeholder="Enter username",
                id="username-input",
                classes="input-field",
            )
            yield Label("Password:", classes="input-label")
            yield Input(
                placeholder="Enter password",
                id="password-input",
                password=True,
                classes="input-field",
            )
            yield Static(id="error-message")
            with Container(id="button-container"):
                yield Button("Login", id="login-button", variant="primary")
                yield Button("Quit", id="quit-button", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "login-button":
            self.attempt_login()
        elif event.button.id == "quit-button":
            self.app.exit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in password input."""
        if event.input.id == "password-input":
            self.attempt_login()

    def attempt_login(self) -> None:
        """Trigger login attempt in a worker thread."""
        username_input = self.query_one("#username-input", Input)
        password_input = self.query_one("#password-input", Input)

        username = username_input.value.strip()
        password = password_input.value

        if not username or not password:
            error_message = self.query_one("#error-message", Static)
            error_message.update("Please enter both username and password")
            return

        self.perform_login_worker(username, password)

    @work(thread=True)
    def perform_login_worker(self, username: str, password: str) -> None:  # noqa: D102
        """Attempt to log in with provided credentials in a thread."""
        try:
            user = User.objects.get(name=username)
            if user.check_password(password):
                set_current_user(username, user.is_admin())
                self.app.call_from_thread(self.login_success)
            else:
                self.app.call_from_thread(self.login_failure)
        except User.DoesNotExist:
            self.app.call_from_thread(self.login_failure)

    def login_success(self) -> None:  # noqa: D102
        """Handle successful login."""
        self.app.switch_screen("main")

    def login_failure(self) -> None:  # noqa: D102
        """Handle login failure."""
        error_message = self.query_one("#error-message", Static)
        password_input = self.query_one("#password-input", Input)
        error_message.update("Invalid username or password")
        password_input.value = ""


class LoginApp(App[None]):
    """Main app with login screen."""

    CSS_PATH = "../tui/tui.css"

    def on_mount(self) -> None:  # noqa: D102
        self.install_screen(SVSTUIScreen(), name="main")
        self.push_screen(LoginScreen())


def run_login_app() -> None:  # noqa: D103
    app = LoginApp()
    app.run()


if __name__ == "__main__":
    run_login_app()
