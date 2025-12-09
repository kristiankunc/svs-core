import sys

from typing import Type, TypeVar, cast

import typer

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from rich import print

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
