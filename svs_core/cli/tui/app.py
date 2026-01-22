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
        name_input = self.query_one("#service-name-input", Input)
        template_select = self.query_one("#template-select", Select)
        domain_input = self.query_one("#domain-input", Input)

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
            user = User.objects.get(name=get_current_username())
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

    def show_error(self, message: str) -> None:  # noqa: D102
        """Display error message."""
        error_widget = self.query_one("#create-error-message", Static)
        error_widget.update(f"Error: {message}")


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
        username_input = self.query_one("#username-input", Input)
        password_input = self.query_one("#password-input", Input)

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
        error_widget = self.query_one("#create-error-message", Static)
        error_widget.update(f"Error: {message}")


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
        import json

        path_input = self.query_one("#template-path-input", Input)
        path = path_input.value.strip()

        if not path:
            self.app.call_from_thread(self.show_error, "Template file path is required")
            return

        if not os.path.exists(path):
            self.app.call_from_thread(self.show_error, "File does not exist")
            return

        try:
            with open(path, "r") as file:
                data = json.load(file)

            Template.import_from_json(data)
            self.app.call_from_thread(self.dismiss, True)
        except (TemplateException, ValidationException) as e:
            self.app.call_from_thread(self.show_error, str(e))

    def show_error(self, message: str) -> None:  # noqa: D102
        """Display error message."""
        error_widget = self.query_one("#import-error-message", Static)
        error_widget.update(f"Error: {message}")


class SVSTUIScreen(Screen[None]):
    """A Textual TUI screen for SVS Core."""

    CSS_PATH = "./tui.css"

    BINDINGS = [
        ("q", "quit", "Quit the application"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self) -> None:
        """Initialize the screen."""
        super().__init__()
        self.selected_service: Service | None = None
        self.selected_template: Template | None = None
        self.selected_user: User | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        with Container(id="left-panel"):
            with Container(id="services-container", classes="box-container"):
                self.services_list = ListView(id="services-list", classes="box")
                yield self.services_list

            with Container(id="templates-container", classes="box-container"):
                self.template_list = ListView(id="templates-list", classes="box")
                yield self.template_list

            if is_current_user_admin():
                with Container(id="users-container", classes="box-container"):
                    self.users_list = ListView(id="users-list", classes="box")
                    yield self.users_list

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
                    yield Button("📋 Logs", id="logs-service-btn", variant="primary")
                    yield Button("🗑 Delete", id="delete-service-btn", variant="error")

                # Template action buttons
                with Horizontal(id="template-actions", classes="action-buttons"):
                    if is_current_user_admin():
                        yield Button(
                            "📥 Import", id="import-template-btn", variant="primary"
                        )
                        yield Button(
                            "🗑 Delete", id="delete-template-btn", variant="error"
                        )

                # User action buttons (admin only)
                if is_current_user_admin():
                    with Horizontal(id="user-actions", classes="action-buttons"):
                        yield Button("🗑 Delete", id="delete-user-btn", variant="error")

                # General action buttons
                with Horizontal(id="general-actions", classes="action-buttons"):
                    yield Button(
                        "➕ New Service", id="create-service-btn", variant="primary"
                    )
                    if is_current_user_admin():
                        yield Button(
                            "➕ New User", id="create-user-btn", variant="primary"
                        )

        yield Footer()

    @work(thread=True)
    def load_homepage(self) -> None:  # noqa: D102
        if self.is_admin:
            services = list(Service.objects.all())
            users = list(User.objects.all())
            self.app.call_from_thread(self.populate_users, users)
        else:
            services = list(Service.objects.filter(user__name=self.current_username))

        templates = list(Template.objects.all())
        self.app.call_from_thread(self.populate_services, services)
        self.app.call_from_thread(self.populate_templates, templates)

    def populate_services(self, services: list[Service]) -> None:  # noqa: D102
        self.services_list.clear()

        for service in services:
            status_icon = "🟢" if service.status == ServiceStatus.RUNNING else "🔴"
            item = ListItem(
                Static(f"{status_icon} {service.name}"), id=f"service-{service.id}"
            )
            self.services_list.append(item)

        services_container = self.query_one("#services-container", Container)
        services_container.border_title = f"Services ({len(services)})"

    def populate_templates(self, templates: list[Template]) -> None:  # noqa: D102
        self.template_list.clear()

        for template in templates:
            item = ListItem(Static(f"📦 {template.name}"), id=f"template-{template.id}")
            self.template_list.append(item)

        templates_container = self.query_one("#templates-container", Container)
        templates_container.border_title = f"Templates ({len(templates)})"

    def populate_users(self, users: list[User]) -> None:  # noqa: D102
        self.users_list.clear()

        for user in users:
            user_icon = "👑" if user.is_admin() else "👤"
            user_display = f"{user_icon} {user.name}"
            item = ListItem(Static(user_display), id=f"user-{user.id}")
            self.users_list.append(item)

        users_container = self.query_one("#users-container", Container)
        users_container.border_title = f"Users ({len(users)})"

    @work(thread=True)
    def fetch_service_details(self, service_id: str) -> None:  # noqa: D102
        """Fetch service details in a thread to avoid blocking the UI."""
        try:
            service = Service.objects.get(id=service_id)
            self.app.call_from_thread(self.set_selected_service, service)
            details = service.pprint()
            self.app.call_from_thread(
                self.display_details_with_title, service.name, details
            )
        except Service.DoesNotExist:
            self.app.call_from_thread(self.display_details, "Service not found")

    @work(thread=True)
    def fetch_template_details(self, template_id: str) -> None:  # noqa: D102
        """Fetch template details in a thread to avoid blocking the UI."""
        try:
            template = Template.objects.get(id=template_id)
            self.app.call_from_thread(self.set_selected_template, template)
            details = template.pprint()
            self.app.call_from_thread(
                self.display_details_with_title, template.name, details
            )
        except Template.DoesNotExist:
            self.app.call_from_thread(self.display_details, "Template not found")

    @work(thread=True)
    def fetch_user_details(self, user_id: str) -> None:  # noqa: D102
        """Fetch user details in a thread to avoid blocking the UI."""
        try:
            user = User.objects.get(id=user_id)
            self.app.call_from_thread(self.set_selected_user, user)
            details = user.pprint()
            self.app.call_from_thread(
                self.display_details_with_title, user.name, details
            )
        except User.DoesNotExist:
            self.app.call_from_thread(self.display_details, "User not found")

    def set_selected_service(self, service: Service) -> None:  # noqa: D102
        """Set the currently selected service and update button visibility."""
        self.selected_service = service
        self.selected_template = None
        self.selected_user = None
        self.update_action_buttons_visibility()

    def set_selected_template(self, template: Template) -> None:  # noqa: D102
        """Set the currently selected template and update button visibility."""
        self.selected_template = template
        self.selected_service = None
        self.selected_user = None
        self.update_action_buttons_visibility()

    def set_selected_user(self, user: User) -> None:  # noqa: D102
        """Set the currently selected user and update button visibility."""
        self.selected_user = user
        self.selected_service = None
        self.selected_template = None
        self.update_action_buttons_visibility()

    def update_action_buttons_visibility(self) -> None:  # noqa: D102
        """Update the visibility of action buttons based on what is selected."""
        service_actions = self.query_one("#service-actions", Container)
        template_actions = self.query_one("#template-actions", Container)
        general_actions = self.query_one("#general-actions", Container)

        # Always show general actions
        general_actions.display = True

        # Show service actions only if a service is selected
        service_actions.display = self.selected_service is not None

        # Show template actions only if a template is selected and user is admin
        if is_current_user_admin():
            template_actions.display = self.selected_template is not None

        # Show user actions only if a user is selected and user is admin
        if is_current_user_admin():
            user_actions = self.query_one("#user-actions", Container)
            user_actions.display = self.selected_user is not None

    def display_details(self, details: str) -> None:  # noqa: D102
        """Update the details panel with the formatted content."""
        details_panel = self.query_one("#details-content", Static)
        details_panel.update(details)

    def display_details_with_title(
        self, title: str, details: str
    ) -> None:  # noqa: D102
        """Update the details panel with title and formatted content."""
        details_panel = self.query_one("#details-content", Static)
        details_panel.border_title = title
        details_panel.update(details)

    def on_list_view_selected(self, message: ListView.Selected) -> None:  # noqa: D102
        """Handle when an item is selected in any ListView."""
        if not message.item or not message.item.id:
            return
        item_id = message.item.id

        if item_id.startswith("service-"):
            service_id = item_id.replace("service-", "")
            self.fetch_service_details(service_id)
        elif item_id.startswith("template-"):
            template_id = item_id.replace("template-", "")
            self.fetch_template_details(template_id)
        elif item_id.startswith("user-"):
            user_id = item_id.replace("user-", "")
            self.fetch_user_details(user_id)

    def on_list_view_highlighted(
        self, message: ListView.Highlighted
    ) -> None:  # noqa: D102
        """Handle when an item is highlighted (scrolled to) in any ListView."""
        if not message.item or not message.item.id:
            return
        item_id = message.item.id

        if item_id.startswith("service-"):
            service_id = item_id.replace("service-", "")
            self.fetch_service_details(service_id)
        elif item_id.startswith("template-"):
            template_id = item_id.replace("template-", "")
            self.fetch_template_details(template_id)
        elif item_id.startswith("user-"):
            user_id = item_id.replace("user-", "")
            self.fetch_user_details(user_id)

    def on_button_pressed(self, event: Button.Pressed) -> None:  # noqa: D102
        """Handle button presses."""
        button_id = event.button.id

        # Service actions
        if button_id == "start-service-btn" and self.selected_service:
            self.start_service()
        elif button_id == "stop-service-btn" and self.selected_service:
            self.stop_service()
        elif button_id == "logs-service-btn" and self.selected_service:
            self.view_service_logs()
        elif button_id == "delete-service-btn" and self.selected_service:
            self.delete_service()

        # Template actions
        elif button_id == "import-template-btn":
            self.import_template()
        elif button_id == "delete-template-btn" and self.selected_template:
            self.delete_template()

        # User actions
        elif button_id == "delete-user-btn" and self.selected_user:
            self.delete_user()

        # General actions
        elif button_id == "create-service-btn":
            self.create_service()
        elif button_id == "create-user-btn":
            self.create_user()

    @work(thread=True)
    def start_service(self) -> None:  # noqa: D102
        """Start the selected service."""
        if not self.selected_service:
            return

        try:
            self.selected_service.start()
            self.app.call_from_thread(
                self.show_success,
                f"Service '{self.selected_service.name}' started successfully",
            )
            self.app.call_from_thread(self.action_refresh)
        except ServiceOperationException as e:
            self.app.call_from_thread(self.show_error, f"Error starting service: {e}")

    @work(thread=True)
    def stop_service(self) -> None:  # noqa: D102
        """Stop the selected service."""
        if not self.selected_service:
            return

        try:
            self.selected_service.stop()
            self.app.call_from_thread(
                self.show_success,
                f"Service '{self.selected_service.name}' stopped successfully",
            )
            self.app.call_from_thread(self.action_refresh)
        except ServiceOperationException as e:
            self.app.call_from_thread(self.show_error, f"Error stopping service: {e}")

    @work(thread=True)
    def view_service_logs(self) -> None:  # noqa: D102
        """View logs for the selected service."""
        if not self.selected_service:
            return

        try:
            logs = self.selected_service.get_logs()
            self.app.call_from_thread(self.show_logs, self.selected_service.name, logs)
        except Exception as e:
            self.app.call_from_thread(self.show_error, f"Error fetching logs: {e}")

    @work(thread=True)
    def delete_service(self) -> None:  # noqa: D102
        """Delete the selected service."""
        if not self.selected_service:
            return

        try:
            service_name = self.selected_service.name
            self.selected_service.delete()
            self.app.call_from_thread(
                self.show_success, f"Service '{service_name}' deleted successfully"
            )
            self.app.call_from_thread(self.action_refresh)
        except Exception as e:
            self.app.call_from_thread(self.show_error, f"Error deleting service: {e}")

    @work(thread=True)
    def delete_template(self) -> None:  # noqa: D102
        """Delete the selected template."""
        if not self.selected_template:
            return

        try:
            template_name = self.selected_template.name
            self.selected_template.delete()
            self.app.call_from_thread(
                self.show_success, f"Template '{template_name}' deleted successfully"
            )
            self.app.call_from_thread(self.action_refresh)
        except Exception as e:
            self.app.call_from_thread(self.show_error, f"Error deleting template: {e}")

    @work(thread=True)
    def delete_user(self) -> None:  # noqa: D102
        """Delete the selected user."""
        if not self.selected_user:
            return

        try:
            user_name = self.selected_user.name
            self.selected_user.delete()
            self.app.call_from_thread(
                self.show_success, f"User '{user_name}' deleted successfully"
            )
            self.app.call_from_thread(self.action_refresh)
        except Exception as e:
            self.app.call_from_thread(self.show_error, f"Error deleting user: {e}")

    def create_service(self) -> None:  # noqa: D102
        """Show the create service modal."""
        templates = list(Template.objects.all())
        self.app.push_screen(CreateServiceModal(templates), self.on_service_created)

    def on_service_created(self, created: bool | None) -> None:  # noqa: D102
        """Handle service creation result."""
        if created:
            self.show_success("Service created successfully")
            self.action_refresh()

    def import_template(self) -> None:  # noqa: D102
        """Show the import template modal."""
        self.app.push_screen(ImportTemplateModal(), self.on_template_imported)

    def on_template_imported(self, imported: bool | None) -> None:  # noqa: D102
        """Handle template import result."""
        if imported:
            self.show_success("Template imported successfully")
            self.action_refresh()

    def create_user(self) -> None:  # noqa: D102
        """Show the create user modal."""
        self.app.push_screen(CreateUserModal(), self.on_user_created)

    def on_user_created(self, created: bool | None) -> None:  # noqa: D102
        """Handle user creation result."""
        if created:
            self.show_success("User created successfully")
            self.action_refresh()

    def show_logs(self, service_name: str, logs: str) -> None:  # noqa: D102
        """Show the logs modal."""
        self.app.push_screen(LogsModal(service_name, logs))

    def show_success(self, message: str) -> None:  # noqa: D102
        """Show success message in the details panel."""
        self.notify(message, title="Success", severity="information")

    def show_error(self, message: str) -> None:  # noqa: D102
        """Show error message in the details panel."""
        self.notify(message, title="Error", severity="error")

    def on_mount(self) -> None:  # noqa: D102
        # Capture user info before starting thread worker
        self.current_username = get_current_username()
        self.is_admin = is_current_user_admin()

        self.title = f"SVS v{version('svs-core')}"
        self.sub_title = f"{self.current_username} {'(admin)' if self.is_admin else ''}"

        # Initialize with no selection
        self.selected_service = None
        self.selected_template = None
        self.selected_user = None

        # Hide all action buttons initially except general actions
        self.update_action_buttons_visibility()

        self.load_homepage()

    async def action_quit(self) -> None:  # noqa: D102
        self.app.exit()

    def action_refresh(self) -> None:  # noqa: D102
        """Refresh the data on the screen."""
        self.selected_service = None
        self.selected_template = None
        self.selected_user = None
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
