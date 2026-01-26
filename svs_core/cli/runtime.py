import os
import sys

import django

from svs_core.cli.state import set_verbose_mode
from svs_core.shared.env_manager import EnvManager
from svs_core.shared.logger import add_verbose_handler, get_logger


def setup_runtime() -> None:
    """Set up the runtime environment for the CLI application."""
    # early verbose detection
    if "-v" in sys.argv or "--verbose" in sys.argv:
        set_verbose_mode(True)
        add_verbose_handler()

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "svs_core.db.settings",
    )

    if EnvManager.get_runtime_environment() != EnvManager.RuntimeEnvironment.TESTING:
        EnvManager.load_env_file()

    django.setup()

    if not EnvManager.get_database_url():
        get_logger(__name__).warning(
            "DATABASE_URL not set. Running without database."
        )
