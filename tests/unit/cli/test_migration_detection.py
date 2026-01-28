"""Test that the CLI migration command works correctly without phantom changes."""

from io import StringIO

import pytest

from django.core.management import call_command


@pytest.mark.unit
@pytest.mark.django_db
class TestMigrationDetection:
    """Test migration detection in CLI commands."""

    def test_migrate_command_no_phantom_changes(self) -> None:
        """Test that migrate command doesn't detect phantom model changes.

        This test ensures that running migrations via call_command (as the
        CLI does) produces the same result as running migrations directly,
        without incorrectly detecting model changes.
        """
        # First, ensure migrations are applied
        out = StringIO()
        call_command("migrate", stdout=out, verbosity=1)
        output = out.getvalue()

        # Should not contain the warning about unapplied changes
        assert "have changes that are not yet reflected" not in output, (
            "Migration command incorrectly detected phantom model changes. "
            f"Output: {output}"
        )

        # Run again to ensure idempotency
        out = StringIO()
        call_command("migrate", stdout=out, verbosity=1)
        output = out.getvalue()

        assert "No migrations to apply" in output or "OK" in output
        assert "have changes that are not yet reflected" not in output

    def test_makemigrations_detects_no_changes(self) -> None:
        """Test that makemigrations doesn't detect any pending changes."""
        out = StringIO()
        call_command("makemigrations", dry_run=True, stdout=out, verbosity=1)
        output = out.getvalue()

        assert (
            "No changes detected" in output
        ), f"makemigrations detected unexpected changes. Output: {output}"
