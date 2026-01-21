import os
import sys

from importlib.metadata import version
from typing import cast

import django

from django.apps import apps as django_apps
from textual import work
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, ListItem, ListView, Static

from svs_core.cli.state import (
    get_current_username,
    is_current_user_admin,
    set_current_user,
)

if not django_apps.ready:
    os.environ["DJANGO_SETTINGS_MODULE"] = "svs_core.db.settings"
    django.setup()

from svs_core.docker.service import Service
from svs_core.docker.template import Template
from svs_core.users.system import SystemUserManager
from svs_core.users.user import User


class ItemSelected:
    """Message for when an item is selected."""

    def __init__(self, item_type: str, item_id: str) -> None:
        """Initialize the message."""
        self.item_type = item_type
        self.item_id = item_id


class SVSTUIScreen(Screen[None]):
    """A Textual TUI screen for SVS Core."""

    CSS_PATH = "./tui.css"

    BINDINGS = [
        ("q", "quit", "Quit the application"),
    ]

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

        yield Static(
            "Details\n\nSelect an item from the left panel to view details here.\n\nUse arrow keys, tab to navigate.",
            id="right-panel",
            classes="box",
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
            item = ListItem(Static(service.name), id=f"service-{service.id}")
            self.services_list.append(item)

        services_container = self.query_one("#services-container", Container)
        services_container.border_title = f"Services ({len(services)})"

    def populate_templates(self, templates: list[Template]) -> None:  # noqa: D102
        self.template_list.clear()

        for template in templates:
            item = ListItem(Static(template.name), id=f"template-{template.id}")
            self.template_list.append(item)

        templates_container = self.query_one("#templates-container", Container)
        templates_container.border_title = f"Templates ({len(templates)})"

    def populate_users(self, users: list[User]) -> None:  # noqa: D102
        self.users_list.clear()

        for user in users:
            user_display = f"{user.name} {'(admin)' if user.is_admin() else '(user)'}"
            item = ListItem(Static(user_display), id=f"user-{user.id}")
            self.users_list.append(item)

        users_container = self.query_one("#users-container", Container)
        users_container.border_title = f"Users ({len(users)})"

    @work(thread=True)
    def fetch_service_details(self, service_id: str) -> None:  # noqa: D102
        """Fetch service details in a thread to avoid blocking the UI."""
        try:
            service = Service.objects.get(id=service_id)
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
            details = user.pprint()
            self.app.call_from_thread(
                self.display_details_with_title, user.name, details
            )
        except User.DoesNotExist:
            self.app.call_from_thread(self.display_details, "User not found")

    def display_details(self, details: str) -> None:  # noqa: D102
        """Update the details panel with the formatted content."""
        details_panel = self.query_one("#right-panel", Static)
        details_panel.update(details)

    def display_details_with_title(
        self, title: str, details: str
    ) -> None:  # noqa: D102
        """Update the details panel with title and formatted content."""
        details_panel = self.query_one("#right-panel", Static)
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

    def on_mount(self) -> None:  # noqa: D102
        # Capture user info before starting thread worker
        self.current_username = get_current_username()
        self.is_admin = is_current_user_admin()

        self.title = f"SVS v{version('svs-core')}"
        self.sub_title = f"{self.current_username} {'(admin)' if self.is_admin else ''}"

        self.load_homepage()

    async def action_quit(self) -> None:  # noqa: D102
        self.app.exit()


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
