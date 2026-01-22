"""Refactored SVS Core TUI with improved reliability and thread safety."""

import json
import os
import sys
from importlib.metadata import version
from pathlib import Path
from typing import cast

import django
from django.apps import apps as django_apps
from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
)

from svs_core.cli.state import (
    get_current_username,
    is_current_user_admin,
    set_current_user,
)
from svs_core.cli.tui.data_access import DataAccessLayer
from svs_core.cli.tui.event_debouncer import EventDebouncer
from svs_core.cli.tui.state_manager import SelectionType, ThreadSafeStateManager

if not django_apps.ready:
    os.environ["DJANGO_SETTINGS_MODULE"] = "svs_core.db.settings"
    django.setup()

from svs_core.db.models import ServiceStatus
from svs_core.docker.service import Service
from svs_core.docker.template import Template
from svs_core.shared.exceptions import (
    AlreadyExistsException,
    ConfigurationException,
    NotFoundException,
    ServiceOperationException,
    TemplateException,
    ValidationException,
)
from svs_core.users.system import SystemUserManager
from svs_core.users.user import (
    InvalidPasswordException,
    InvalidUsernameException,
    User,
)


class CreateServiceModal(ModalScreen[bool]):
    """Modal screen for creating a new service."""

    def __init__(self, templates: list[Template]) -> None:
        """Initialize the modal."""
        super().__init__()
        self.templates = templates

    def compose(self) -> ComposeResult:
        """Create child widgets for the modal."""
        with Vertical(id="create-service-dialog"):
            yield Label("Create New Service", id="dialog-title")
            yield Label("Service Name:")
            yield Input(placeholder="Enter service name", id="service-name-input")
            yield Label("Template:")
            template_options = [
                (f"{t.name} ({t.type})", str(t.id)) for t in self.templates
            ]
            yield Select(
                options=template_options,
                id="template-select",
                prompt="Select a template",
            )
            yield Label("Domain (optional):")
            yield Input(placeholder="Enter domain (optional)", id="domain-input")
            yield Static(id="create-error-message", classes="error-message")
            with Horizontal(id="dialog-buttons"):
                yield Button("Create", id="create-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-btn":
            self.dismiss(False)
        elif event.button.id == "create-btn":
            self.create_service()

    @work(thread=True)
    def create_service(self) -> None:  # noqa: D102
        """Create the service in a worker thread."""
        try:
            name_input = self.query_one("#service-name-input", Input)
            template_select = self.query_one("#template-select", Select)
            domain_input = self.query_one("#domain-input", Input)
        except Exception:
            # UI may have changed, abort
            return

        name = name_input.value.strip()
        template_id = template_select.value
        domain = domain_input.value.strip() or None

        if not name:
            self.app.call_from_thread(self.show_error, "Service name is required")
            return

        if template_id == Select.BLANK:
            self.app.call_from_thread(self.show_error, "Please select a template")
            return

        try:
            from svs_core.users.user import User
            from svs_core.cli.state import get_current_username
            
            username = get_current_username()
            if not username:
                self.app.call_from_thread(self.show_error, "No user logged in")
                return
            
            user = User.objects.get(name=username)
            # Type assertion for template_id which should be a string at this point
            template_id_int = int(str(template_id))
            Service.create_from_template(
                name,
                template_id_int,
                user,
                domain=domain,
            )
            self.app.call_from_thread(self.dismiss, True)
        except (ValidationException, ConfigurationException, NotFoundException) as e:
            self.app.call_from_thread(self.show_error, str(e))
        except Exception as e:
            self.app.call_from_thread(self.show_error, f"Error: {e}")

    def show_error(self, message: str) -> None:  # noqa: D102
        """Display error message."""
        try:
            error_widget = self.query_one("#create-error-message", Static)
            error_widget.update(f"Error: {message}")
        except Exception:
            # UI may have changed, ignore
            pass


class CreateUserModal(ModalScreen[bool]):
    """Modal screen for creating a new user (admin only)."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the modal."""
        with Vertical(id="create-user-dialog"):
            yield Label("Create New User", id="dialog-title")
            yield Label("Username:")
            yield Input(placeholder="Enter username", id="username-input")
            yield Label("Password:")
            yield Input(
                placeholder="Enter password", id="password-input", password=True
            )
            yield Static(id="create-error-message", classes="error-message")
            with Horizontal(id="dialog-buttons"):
                yield Button("Create", id="create-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-btn":
            self.dismiss(False)
        elif event.button.id == "create-btn":
            self.create_user()

    @work(thread=True)
    def create_user(self) -> None:  # noqa: D102
        """Create the user in a worker thread."""
        try:
            username_input = self.query_one("#username-input", Input)
            password_input = self.query_one("#password-input", Input)
        except Exception:
            return

        username = username_input.value.strip()
        password = password_input.value

        if not username or not password:
            self.app.call_from_thread(
                self.show_error, "Username and password are required"
            )
            return

        try:
            User.create(username, password)
            self.app.call_from_thread(self.dismiss, True)
        except (
            InvalidUsernameException,
            InvalidPasswordException,
            AlreadyExistsException,
        ) as e:
            self.app.call_from_thread(self.show_error, str(e))

    def show_error(self, message: str) -> None:  # noqa: D102
        """Display error message."""
        try:
            error_widget = self.query_one("#create-error-message", Static)
            error_widget.update(f"Error: {message}")
        except Exception:
            pass


class LogsModal(ModalScreen[None]):
    """Modal screen for displaying service logs."""

    def __init__(self, service_name: str, logs: str) -> None:
        """Initialize the modal."""
        super().__init__()
        self.service_name = service_name
        self.logs = logs

    def compose(self) -> ComposeResult:
        """Create child widgets for the modal."""
        with Vertical(id="logs-dialog"):
            yield Label(f"Logs for {self.service_name}", id="dialog-title")
            yield Static(self.logs, id="logs-content", classes="logs-content")
            with Horizontal(id="dialog-buttons"):
                yield Button("Close", id="close-btn", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "close-btn":
            self.dismiss()


class ImportTemplateModal(ModalScreen[bool]):
    """Modal screen for importing a template (admin only)."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the modal."""
        with Vertical(id="import-template-dialog"):
            yield Label("Import Template", id="dialog-title")
            yield Label("Template File Path:")
            yield Input(
                placeholder="Enter template file path (.json)", id="template-path-input"
            )
            yield Static(id="import-error-message", classes="error-message")
            with Horizontal(id="dialog-buttons"):
                yield Button("Import", id="import-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-btn":
            self.dismiss(False)
        elif event.button.id == "import-btn":
            self.import_template()

    @work(thread=True)
    def import_template(self) -> None:  # noqa: D102
        """Import the template in a worker thread."""
        try:
            path_input = self.query_one("#template-path-input", Input)
        except Exception:
            return

        path_str = path_input.value.strip()

        if not path_str:
            self.app.call_from_thread(self.show_error, "Template file path is required")
            return

        path = Path(path_str)
        if not path.exists():
            self.app.call_from_thread(self.show_error, "File does not exist")
            return

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            Template.import_from_json(data)
            self.app.call_from_thread(self.dismiss, True)
        except (
            TemplateException,
            ValidationException,
            FileNotFoundError,
            json.JSONDecodeError,
        ) as e:
            self.app.call_from_thread(self.show_error, str(e))

    def show_error(self, message: str) -> None:  # noqa: D102
        """Display error message."""
        try:
            error_widget = self.query_one("#import-error-message", Static)
            error_widget.update(f"Error: {message}")
        except Exception:
            pass


class ConfirmationModal(ModalScreen[bool]):
    """Modal screen for confirming destructive actions."""

    def __init__(self, title: str, message: str) -> None:
        """Initialize the modal.
        
        Args:
            title: Title of the confirmation dialog.
            message: Message to display.
        """
        super().__init__()
        self.confirm_title = title
        self.confirm_message = message

    def compose(self) -> ComposeResult:
        """Create child widgets for the modal."""
        with Vertical(id="confirmation-dialog"):
            yield Label(self.confirm_title, id="dialog-title")
            yield Label(self.confirm_message)
            with Horizontal(id="dialog-buttons"):
                yield Button("Confirm", id="confirm-btn", variant="warning")
                yield Button("Cancel", id="cancel-btn", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-btn":
            self.dismiss(False)
        elif event.button.id == "confirm-btn":
            self.dismiss(True)


class SVSTUIScreen(Screen[None]):
    """A Textual TUI screen for SVS Core with improved reliability."""

    CSS_PATH = "./tui.css"

    BINDINGS = [
        ("q", "quit", "Quit the application"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self) -> None:
        """Initialize the screen."""
        super().__init__()
        self.state_manager = ThreadSafeStateManager()
        self.data_access = DataAccessLayer(cache_ttl=60.0)
        self.event_debouncer = EventDebouncer(delay_seconds=0.15)
        self.current_username = ""
        self.is_admin = False
        self.operation_count = 0  # Track number of ongoing operations

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        with Vertical(id="left-panel"):
            with Container(id="services-container", classes="box-container"):
                self.services_list = ListView(id="services-list", classes="box")
                yield self.services_list
            
            # Services section action button
            with Horizontal(id="services-actions", classes="section-actions"):
                yield Button(
                    "➕ New Service", id="create-service-btn", variant="primary"
                )

            with Container(id="templates-container", classes="box-container"):
                self.template_list = ListView(id="templates-list", classes="box")
                yield self.template_list
            
            # Templates section action button
            if is_current_user_admin():
                with Horizontal(id="templates-actions", classes="section-actions"):
                    yield Button(
                        "📥 Import Template", id="import-template-direct-btn", variant="primary"
                    )

            if is_current_user_admin():
                with Container(id="users-container", classes="box-container"):
                    self.users_list = ListView(id="users-list", classes="box")
                    yield self.users_list
                
                # Users section action button
                with Horizontal(id="users-actions", classes="section-actions"):
                    yield Button(
                        "➕ New User", id="create-user-btn", variant="primary"
                    )

        with Vertical(id="right-panel"):
            yield Static(
                "Details\n\nSelect an item from the left panel to view details here.",
                id="details-content",
                classes="box",
            )

            with Container(id="action-buttons-container"):
                # Service action buttons
                with Horizontal(id="service-actions", classes="action-buttons"):
                    yield Button("▶ Start", id="start-service-btn", variant="success")
                    yield Button("⏸ Stop", id="stop-service-btn", variant="warning")
                    yield Button("⚙ Restart", id="restart-service-btn", variant="warning")
                    yield Button("📋 Logs", id="logs-service-btn", variant="primary")
                    yield Button("🗑 Delete", id="delete-service-btn", variant="error")

                # Template action buttons - only for admins
                if is_current_user_admin():
                    with Horizontal(id="template-actions", classes="action-buttons"):
                        yield Button(
                            "🗑 Delete", id="delete-template-btn", variant="error"
                        )

                # User action buttons - only for admins
                if is_current_user_admin():
                     with Horizontal(id="user-actions", classes="action-buttons"):
                         yield Button("🔐 Reset Password", id="reset-password-btn", variant="warning")
                         yield Button("🗑 Delete", id="delete-user-btn", variant="error")

        # Status indicator at the bottom
        yield Static("", id="status-indicator", classes="status-indicator")
        yield Footer()

    @work(thread=True)
    def load_homepage(self) -> None:  # noqa: D102
        """Load data without blocking UI."""
        try:
            if self.is_admin:
                services = self.data_access.get_all_services()
                users = self.data_access.get_all_users()
                self.app.call_from_thread(self.populate_users, users)
            else:
                services = self.data_access.get_all_services(
                    filter_username=self.current_username
                )

            templates = self.data_access.get_all_templates()
            self.app.call_from_thread(self.populate_services, services)
            self.app.call_from_thread(self.populate_templates, templates)
        except Exception as e:
            self.app.call_from_thread(self.show_error, f"Error loading data: {e}")

    def populate_services(self, services: list[Service]) -> None:  # noqa: D102
        """Populate services list."""
        try:
            self.services_list.clear()

            for service in services:
                status_icon = "🟢" if service.status == ServiceStatus.RUNNING else "🔴"
                item = ListItem(Label(f"{status_icon} {service.name}"))
                item.data = service.id  # type: ignore[attr-defined]
                self.services_list.append(item)

            services_container = self.query_one("#services-container", Container)
            services_container.border_title = f"Services ({len(services)})"
        except Exception:
            # UI may have changed, ignore
            pass

    def populate_templates(self, templates: list[Template]) -> None:  # noqa: D102
        """Populate templates list."""
        try:
            self.template_list.clear()

            for template in templates:
                item = ListItem(Label(f"📦 {template.name}"))
                item.data = template.id  # type: ignore[attr-defined]
                self.template_list.append(item)

            templates_container = self.query_one("#templates-container", Container)
            templates_container.border_title = f"Templates ({len(templates)})"
        except Exception:
            pass

    def populate_users(self, users: list[User]) -> None:  # noqa: D102
        """Populate users list."""
        try:
            self.users_list.clear()

            for user in users:
                user_icon = "👑" if user.is_admin() else "👤"
                user_display = f"{user_icon} {user.name}"
                item = ListItem(Label(user_display))
                item.data = user.id  # type: ignore[attr-defined]
                self.users_list.append(item)

            users_container = self.query_one("#users-container", Container)
            users_container.border_title = f"Users ({len(users)})"
        except Exception:
            pass

    @work(thread=True)
    def fetch_service_details(self, service_id: int) -> None:  # noqa: D102
        """Fetch service details without blocking."""
        try:
            service = self.data_access.get_service(service_id)
            if service:
                self.app.call_from_thread(self.set_selected_service, service)
                details = service.pprint()
                self.app.call_from_thread(
                    self.display_details_with_title, service.name, details
                )
            else:
                self.app.call_from_thread(self.display_details, "Service not found")
        except Exception as e:
            self.app.call_from_thread(self.display_details, f"Error: {e}")

    @work(thread=True)
    def fetch_template_details(self, template_id: int) -> None:  # noqa: D102
        """Fetch template details without blocking."""
        try:
            template = self.data_access.get_template(template_id)
            if template:
                self.app.call_from_thread(self.set_selected_template, template)
                details = template.pprint()
                self.app.call_from_thread(
                    self.display_details_with_title, template.name, details
                )
            else:
                self.app.call_from_thread(self.display_details, "Template not found")
        except Exception as e:
            self.app.call_from_thread(self.display_details, f"Error: {e}")

    @work(thread=True)
    def fetch_user_details(self, user_id: int) -> None:  # noqa: D102
        """Fetch user details without blocking."""
        try:
            user = self.data_access.get_user(user_id)
            if user:
                self.app.call_from_thread(self.set_selected_user, user)
                details = user.pprint()
                self.app.call_from_thread(
                    self.display_details_with_title, user.name, details
                )
            else:
                self.app.call_from_thread(self.display_details, "User not found")
        except Exception as e:
            self.app.call_from_thread(self.display_details, f"Error: {e}")

    def set_selected_service(self, service: Service) -> None:  # noqa: D102
        """Safely set selected service."""
        self.state_manager.set_selection(SelectionType.SERVICE, service.id)
        self.update_action_buttons_visibility()

    def set_selected_template(self, template: Template) -> None:  # noqa: D102
        """Safely set selected template."""
        self.state_manager.set_selection(SelectionType.TEMPLATE, template.id)
        self.update_action_buttons_visibility()

    def set_selected_user(self, user: User) -> None:  # noqa: D102
        """Safely set selected user."""
        self.state_manager.set_selection(SelectionType.USER, user.id)
        self.update_action_buttons_visibility()

    def update_action_buttons_visibility(self) -> None:  # noqa: D102
        """Update button visibility based on selection."""
        try:
            selection = self.state_manager.get_selection()
            service_actions = self.query_one("#service-actions", Horizontal)
            template_actions = self.query_one("#template-actions", Horizontal)
            user_actions = self.query_one("#user-actions", Horizontal)

            # Show service actions only when a service is selected
            service_actions.display = selection.type == SelectionType.SERVICE

            # Show template/user actions only for admins and when appropriate selection
            if self.is_admin:
                template_actions.display = selection.type == SelectionType.TEMPLATE
                user_actions.display = selection.type == SelectionType.USER
        except Exception:
            pass

    def display_details(self, details: str) -> None:  # noqa: D102
        """Update the details panel."""
        try:
            details_panel = self.query_one("#details-content", Static)
            details_panel.update(details)
        except Exception:
            pass

    def display_details_with_title(self, title: str, details: str) -> None:  # noqa: D102
        """Update the details panel with title."""
        try:
            details_panel = self.query_one("#details-content", Static)
            details_panel.border_title = title
            details_panel.update(details)
        except Exception:
            pass

    def on_list_view_selected(self, message: ListView.Selected) -> None:  # noqa: D102
        """Handle item selection - debounced."""
        if not message.item or not hasattr(message.item, "data"):
            return

        item_id = int(message.item.data)  # type: ignore[attr-defined]
        list_view_id = message.list_view.id

        # Debounce to prevent rapid cascading queries
        if list_view_id == "services-list":
            self.event_debouncer.debounce(
                "service_detail", lambda: self.fetch_service_details(item_id)
            )
        elif list_view_id == "templates-list":
            self.event_debouncer.debounce(
                "template_detail", lambda: self.fetch_template_details(item_id)
            )
        elif list_view_id == "users-list":
            self.event_debouncer.debounce(
                "user_detail", lambda: self.fetch_user_details(item_id)
            )

    def on_list_view_highlighted(
        self, message: ListView.Highlighted
    ) -> None:  # noqa: D102
        """Handle item highlighting - don't fetch details, just update selection display.

        Scrolling should not trigger database queries.
        """
        # Intentionally empty - scrolling should not cause queries
        pass

    def on_button_pressed(self, event: Button.Pressed) -> None:  # noqa: D102
        """Handle button presses."""
        button_id = event.button.id
        selection = self.state_manager.get_selection()

        # Service actions
        if button_id == "start-service-btn" and selection.type == SelectionType.SERVICE:
            self.start_service(selection.item_id)
        elif button_id == "stop-service-btn" and selection.type == SelectionType.SERVICE:
            self.stop_service(selection.item_id)
        elif button_id == "restart-service-btn" and selection.type == SelectionType.SERVICE:
            self.restart_service(selection.item_id)
        elif button_id == "logs-service-btn" and selection.type == SelectionType.SERVICE:
            self.view_service_logs(selection.item_id)
        elif button_id == "delete-service-btn" and selection.type == SelectionType.SERVICE:
            self.delete_service(selection.item_id)

        # Template actions
        elif button_id == "import-template-btn" or button_id == "import-template-direct-btn":
            self.import_template()
        elif button_id == "delete-template-btn" and selection.type == SelectionType.TEMPLATE:
            self.delete_template(selection.item_id)

        # User actions
        elif button_id == "delete-user-btn" and selection.type == SelectionType.USER:
            self.delete_user(selection.item_id)
        elif button_id == "reset-password-btn" and selection.type == SelectionType.USER:
            self.reset_user_password(selection.item_id)

        # Section-specific create actions
        elif button_id == "create-service-btn":
            self.create_service()
        elif button_id == "create-user-btn":
            self.create_user()

    @work(thread=True)
    def start_service(self, service_id: int | None) -> None:  # noqa: D102
        """Start service with operation guard."""
        if service_id is None:
            return

        if not self.state_manager.start_operation():
            self.app.call_from_thread(
                self.show_error, "Operation already in progress"
            )
            return

        try:
            service = self.data_access.get_service(service_id)
            if service:
                self.app.call_from_thread(self.set_status, f"⏳ Starting service '{service.name}'...")
                service.start()
                self.data_access.invalidate_service_cache(service_id)
                self.app.call_from_thread(
                    self.show_success, f"Service '{service.name}' started"
                )
                self.app.call_from_thread(self.clear_status)
                self.app.call_from_thread(self.action_refresh)
        except ServiceOperationException as e:
            self.app.call_from_thread(self.show_error, f"Error starting service: {e}")
            self.app.call_from_thread(self.clear_status)
        finally:
            self.state_manager.end_operation()

    @work(thread=True)
    def stop_service(self, service_id: int | None) -> None:  # noqa: D102
        """Stop service with operation guard."""
        if service_id is None:
            return

        if not self.state_manager.start_operation():
            self.app.call_from_thread(
                self.show_error, "Operation already in progress"
            )
            return

        try:
            service = self.data_access.get_service(service_id)
            if service:
                self.app.call_from_thread(self.set_status, f"⏳ Stopping service '{service.name}'...")
                service.stop()
                self.data_access.invalidate_service_cache(service_id)
                self.app.call_from_thread(
                    self.show_success, f"Service '{service.name}' stopped"
                )
                self.app.call_from_thread(self.clear_status)
                self.app.call_from_thread(self.action_refresh)
        except ServiceOperationException as e:
            self.app.call_from_thread(self.show_error, f"Error stopping service: {e}")
            self.app.call_from_thread(self.clear_status)
        finally:
            self.state_manager.end_operation()

    @work(thread=True)
    def view_service_logs(self, service_id: int | None) -> None:  # noqa: D102
        """View service logs without blocking."""
        if service_id is None:
            return

        try:
            service = self.data_access.get_service(service_id)
            if service:
                logs = service.get_logs()
                self.app.call_from_thread(self.show_logs, service.name, logs)
        except Exception as e:
             self.app.call_from_thread(self.show_error, f"Error fetching logs: {e}")

    def delete_service(self, service_id: int | None) -> None:  # noqa: D102
        """Delete service - show confirmation first."""
        if service_id is None:
            return

        try:
            service = self.data_access.get_service(service_id)
            if service:
                self.app.push_screen(
                    ConfirmationModal(
                        "Delete Service",
                        f"Are you sure you want to delete service '{service.name}'?\nThis action cannot be undone."
                    ),
                    lambda confirmed: self._perform_delete_service(service_id) if confirmed else None
                )
        except Exception as e:
            self.show_error(f"Error: {e}")

    @work(thread=True)
    def _perform_delete_service(self, service_id: int) -> None:  # noqa: D102
        """Actually delete the service after confirmation."""
        if not self.state_manager.start_operation():
            self.app.call_from_thread(
                self.show_error, "Operation already in progress"
            )
            return

        try:
            service = self.data_access.get_service(service_id)
            if service:
                service_name = service.name
                service.delete()
                self.data_access.invalidate_service_cache(service_id)
                self.app.call_from_thread(
                    self.show_success, f"Service '{service_name}' deleted"
                )
                self.app.call_from_thread(self.action_refresh)
        except Exception as e:
            self.app.call_from_thread(self.show_error, f"Error deleting service: {e}")
        finally:
            self.state_manager.end_operation()

    @work(thread=True)
    def restart_service(self, service_id: int | None) -> None:  # noqa: D102
        """Restart service with operation guard."""
        if service_id is None:
            return

        if not self.state_manager.start_operation():
            self.app.call_from_thread(
                self.show_error, "Operation already in progress"
            )
            return

        try:
            service = self.data_access.get_service(service_id)
            if service:
                self.app.call_from_thread(self.set_status, f"⏳ Restarting service '{service.name}'...")
                service.stop()
                service.start()
                self.data_access.invalidate_service_cache(service_id)
                self.app.call_from_thread(
                    self.show_success, f"Service '{service.name}' restarted"
                )
                self.app.call_from_thread(self.clear_status)
                self.app.call_from_thread(self.action_refresh)
        except ServiceOperationException as e:
            self.app.call_from_thread(self.show_error, f"Error restarting service: {e}")
            self.app.call_from_thread(self.clear_status)
        finally:
             self.state_manager.end_operation()

    @work(thread=True)
    def delete_template(self, template_id: int | None) -> None:  # noqa: D102
        """Delete template - show confirmation first."""
        if template_id is None:
            return

        try:
            template = self.data_access.get_template(template_id)
            if template:
                self.app.push_screen(
                    ConfirmationModal(
                        "Delete Template",
                        f"Are you sure you want to delete template '{template.name}'?\nThis action cannot be undone."
                    ),
                    lambda confirmed: self._perform_delete_template(template_id) if confirmed else None
                )
        except Exception as e:
            self.show_error(f"Error: {e}")

    @work(thread=True)
    def _perform_delete_template(self, template_id: int) -> None:  # noqa: D102
        """Actually delete the template after confirmation."""
        if not self.state_manager.start_operation():
            self.app.call_from_thread(
                self.show_error, "Operation already in progress"
            )
            return

        try:
            template = self.data_access.get_template(template_id)
            if template:
                template_name = template.name
                template.delete()
                self.data_access.invalidate_template_cache(template_id)
                self.app.call_from_thread(
                    self.show_success, f"Template '{template_name}' deleted"
                )
                self.app.call_from_thread(self.action_refresh)
        except Exception as e:
            self.app.call_from_thread(self.show_error, f"Error deleting template: {e}")
        finally:
             self.state_manager.end_operation()

    @work(thread=True)
    def delete_user(self, user_id: int | None) -> None:  # noqa: D102
        """Delete user - show confirmation first."""
        if user_id is None:
            return

        try:
            user = self.data_access.get_user(user_id)
            if user:
                self.app.push_screen(
                    ConfirmationModal(
                        "Delete User",
                        f"Are you sure you want to delete user '{user.name}'?\nThis action cannot be undone."
                    ),
                    lambda confirmed: self._perform_delete_user(user_id) if confirmed else None
                )
        except Exception as e:
            self.show_error(f"Error: {e}")

    @work(thread=True)
    def _perform_delete_user(self, user_id: int) -> None:  # noqa: D102
        """Actually delete the user after confirmation."""
        if not self.state_manager.start_operation():
            self.app.call_from_thread(
                self.show_error, "Operation already in progress"
            )
            return

        try:
            user = self.data_access.get_user(user_id)
            if user:
                user_name = user.name
                user.delete()
                self.data_access.invalidate_user_cache(user_id)
                self.app.call_from_thread(
                    self.show_success, f"User '{user_name}' deleted"
                )
                self.app.call_from_thread(self.action_refresh)
        except Exception as e:
            self.app.call_from_thread(self.show_error, f"Error deleting user: {e}")
        finally:
             self.state_manager.end_operation()

    @work(thread=True)
    def reset_user_password(self, user_id: int | None) -> None:  # noqa: D102
        """Reset user password - show confirmation first."""
        if user_id is None:
            return

        try:
            user = self.data_access.get_user(user_id)
            if user:
                self.app.push_screen(
                    ConfirmationModal(
                        "Reset Password",
                        f"Are you sure you want to reset password for user '{user.name}'?"
                    ),
                    lambda confirmed: self._perform_reset_user_password(user_id) if confirmed else None
                )
        except Exception as e:
            self.show_error(f"Error: {e}")

    @work(thread=True)
    def _perform_reset_user_password(self, user_id: int) -> None:  # noqa: D102
        """Actually reset the user password after confirmation."""
        if not self.state_manager.start_operation():
            self.app.call_from_thread(
                self.show_error, "Operation already in progress"
            )
            return

        try:
            user = self.data_access.get_user(user_id)
            if user:
                # Generate a temporary password
                import secrets
                import string
                
                temp_password = "".join(
                    secrets.choice(string.ascii_letters + string.digits)
                    for _ in range(12)
                )
                user.set_password(temp_password)
                user.save()
                self.data_access.invalidate_user_cache(user_id)
                
                # Show the temporary password
                self.app.call_from_thread(
                    self.show_success,
                    f"Password reset for '{user.name}'. New password: {temp_password}"
                )
                self.app.call_from_thread(self.action_refresh)
        except Exception as e:
            self.app.call_from_thread(self.show_error, f"Error resetting password: {e}")
        finally:
            self.state_manager.end_operation()

    def create_service(self) -> None:  # noqa: D102
        """Show the create service modal."""
        self.show_create_service_modal()

    @work(thread=True)
    def show_create_service_modal(self) -> None:  # noqa: D102
        """Fetch templates and show modal."""
        try:
            templates = self.data_access.get_all_templates()
            self.app.call_from_thread(self._push_create_service_modal, templates)
        except Exception as e:
            self.app.call_from_thread(self.show_error, f"Error loading templates: {e}")

    def _push_create_service_modal(
        self, templates: list[Template]
    ) -> None:  # noqa: D102
        """Push the create service modal screen."""
        self.app.push_screen(CreateServiceModal(templates), self.on_service_created)

    def on_service_created(self, created: bool | None) -> None:  # noqa: D102
        """Handle service creation."""
        if created:
            self.show_success("Service created successfully")
            self.action_refresh()

    def import_template(self) -> None:  # noqa: D102
        """Show the import template modal."""
        self.app.push_screen(ImportTemplateModal(), self.on_template_imported)

    def on_template_imported(self, imported: bool | None) -> None:  # noqa: D102
        """Handle template import."""
        if imported:
            self.show_success("Template imported successfully")
            self.action_refresh()

    def create_user(self) -> None:  # noqa: D102
        """Show the create user modal."""
        self.app.push_screen(CreateUserModal(), self.on_user_created)

    def on_user_created(self, created: bool | None) -> None:  # noqa: D102
         """Handle user creation."""
         if created:
             self.show_success("User created successfully")
             self.action_refresh()

    def show_logs(self, service_name: str, logs: str) -> None:  # noqa: D102
        """Show the logs modal."""
        self.app.push_screen(LogsModal(service_name, logs))

    def show_success(self, message: str) -> None:  # noqa: D102
        """Show success message."""
        self.notify(message, title="Success", severity="information")

    def show_error(self, message: str) -> None:  # noqa: D102
        """Show error message."""
        self.notify(message, title="Error", severity="error")

     def set_status(self, message: str) -> None:  # noqa: D102
         """Show status message at the bottom of the screen."""
         try:
             status_widget = self.query_one("#status-indicator", Static)
             status_widget.update(message)
         except Exception:
             # UI may have changed, ignore
             pass

     def clear_status(self) -> None:  # noqa: D102
         """Clear status message."""
         try:
             status_widget = self.query_one("#status-indicator", Static)
             status_widget.update("")
         except Exception:
             # UI may have changed, ignore
             pass

     def on_mount(self) -> None:  # noqa: D102
         """Initialize screen."""
         self.current_username = get_current_username()
         self.is_admin = is_current_user_admin()

         # If no user is logged in, show error and exit
         if not self.current_username:
             self.show_error("No user logged in. Please run: sudo svs user create <username> <password>")
             self.app.exit(code=1)
             return

         self.title = f"SVS v{version('svs-core')}"
         self.sub_title = f"{self.current_username} {'(admin)' if self.is_admin else ''}"

         self.update_action_buttons_visibility()
         self.load_homepage()

    async def action_quit(self) -> None:  # noqa: D102
        """Quit the application."""
        self.event_debouncer.cancel_all()
        self.app.exit()

    def action_refresh(self) -> None:  # noqa: D102
        """Refresh data on screen."""
        self.state_manager.clear_selection()
        self.event_debouncer.cancel_all()
        self.data_access.invalidate_all()
        self.update_action_buttons_visibility()
        self.load_homepage()


def run_tui_app() -> None:  # noqa: D103
    from textual.app import App

    class TUIApp(App[None]):
        """Main TUI application."""

        def on_mount(self) -> None:  # noqa: D102
            self.push_screen(SVSTUIScreen())

    app = TUIApp()
    app.run()


if __name__ == "__main__":
    username = SystemUserManager.get_system_username()
    user = User.objects.filter(name=username).first()

    if not user:
        print(
            f"You are running as system user '{username}', but no matching SVS user was found."
        )
        sys.exit(1)

    is_admin = cast(User, user).is_admin() if user else False
    if user:
        set_current_user(user.name, is_admin)

    run_tui_app()
