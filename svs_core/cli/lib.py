import sys

from typing import TYPE_CHECKING, Literal, Type, TypeVar, Union, cast

import typer

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from rich import print

from svs_core.cli.state import get_current_username, is_current_user_admin

T = TypeVar("T", bound=Model)


def get_or_exit(model: Type[T], **lookup: object) -> T:
    """Retrieve a model instance by lookup fields or exit if not found.

    Args:
        model(Type[T]): The Django model class to query.
        **lookup(object): Field lookups to filter the model.

    Example:
        user = get_or_exit(UserModel, name="alice")
    """
    try:
        return cast(T, model.objects.get(**lookup))
    except ObjectDoesNotExist:
        where = ", ".join(f"{k}={v!r}" for k, v in lookup.items())
        print(f"{model.__name__} with {where} not found.", file=sys.stderr)
        raise typer.Exit(1)


def confirm_action(prompt: str) -> bool:
    """Prompt the user to confirm an action.

    Args:
        prompt (str): The confirmation message to display.

    Returns:
        bool: True if the user confirms, False otherwise.
    """
    response = input(f"{prompt} (y/N): ").strip().lower()
    return response == "y"


def _complete(
    object: Type[Model],
    incomplete: str,
    key: Literal["id", "name"] = "id",
    owner_check: str = "user__name",
    help_description_key: str = "name",
) -> list[tuple[str, str]]:

    try:
        if is_current_user_admin():
            items = object.objects.filter(**{f"{key}__startswith": incomplete})
            return [
                (str(getattr(item, key)), str(getattr(item, help_description_key)))
                for item in items
            ]

        current_username = get_current_username()
        if current_username is None:
            return []

        if owner_check:
            items = object.objects.filter(
                **{
                    f"{owner_check}": current_username,
                    f"{key}__startswith": incomplete,
                }
            )
        else:
            items = object.objects.filter(**{f"{key}__startswith": incomplete})

        return [
            (str(getattr(item, key)), str(getattr(item, help_description_key)))
            for item in items
        ]
    except Exception:
        return []


def username_autocomplete(incomplete: str) -> list[tuple[str, str]]:
    """Autocomplete usernames for CLI commands."""
    from svs_core.users.user import User

    return _complete(User, incomplete, key="name", owner_check="name")


def service_id_autocomplete(incomplete: str) -> list[tuple[str, str]]:
    """Autocomplete service IDs for CLI commands."""
    from svs_core.docker.service import Service

    return _complete(Service, incomplete, key="id", owner_check="user__name")


def template_id_autocomplete(incomplete: str) -> list[tuple[str, str]]:
    """Autocomplete template IDs for CLI commands."""
    from svs_core.docker.template import Template

    return _complete(Template, incomplete, key="id", owner_check="")


def git_source_id_autocomplete(incomplete: str) -> list[tuple[str, str]]:
    """Autocomplete git source IDs for CLI commands."""
    from svs_core.shared.git_source import GitSource

    return _complete(GitSource, incomplete, key="id", owner_check="service__user__name")
