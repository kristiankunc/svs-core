from unittest.mock import Mock

import pytest

from pytest_mock import MockerFixture

from svs_core.migrations.migrator import Migration, Migrator, PackageVersion


@pytest.mark.unit
class TestMigrator:
    """Test suite for Migrator class."""

    def test_get_current_package_version_returns_package_version(self) -> None:
        """Test that get_current_package_version returns a PackageVersion
        instance."""
        version = Migrator.get_current_package_version()
        assert isinstance(version, PackageVersion)
        assert version.major >= 0
        assert version.minor >= 0
        assert version.patch >= 0

    def test_run_no_migrations_when_current_version_less_than_migration(
        self, mocker: MockerFixture
    ) -> None:
        """Test that migrations don't run if current version is less than
        migration version."""
        mocker.patch("svs_core.migrations.migrator.version", return_value="0.10.0")

        mock_migration_func = Mock()
        test_migrations = [
            Migration("test-migration", PackageVersion("0.15.0"), mock_migration_func),
        ]

        original_migrations = Migrator.migrations
        try:
            Migrator.migrations = test_migrations
            Migrator.run(PackageVersion("0.0.0"))

            mock_migration_func.assert_not_called()
        finally:
            Migrator.migrations = original_migrations

    def test_run_no_migrations_when_migration_version_not_greater_than_last_known(
        self, mocker: MockerFixture
    ) -> None:
        """Test that migrations don't run if migration version is not greater
        than last known."""
        mocker.patch("svs_core.migrations.migrator.version", return_value="0.20.0")

        mock_migration_func = Mock()
        test_migrations = [
            Migration("test-migration", PackageVersion("0.15.0"), mock_migration_func),
        ]

        original_migrations = Migrator.migrations
        try:
            Migrator.migrations = test_migrations
            Migrator.run(PackageVersion("0.15.0"))

            mock_migration_func.assert_not_called()
        finally:
            Migrator.migrations = original_migrations

    def test_run_migration_when_conditions_met(self, mocker: MockerFixture) -> None:
        """Test that migration runs when current version >= migration version
        and migration version > last known."""
        mocker.patch("svs_core.migrations.migrator.version", return_value="0.15.0")

        mock_migration_func = Mock()
        test_migrations = [
            Migration("test-migration", PackageVersion("0.15.0"), mock_migration_func),
        ]

        original_migrations = Migrator.migrations
        try:
            Migrator.migrations = test_migrations
            Migrator.run(PackageVersion("0.10.0"))

            mock_migration_func.assert_called_once()
        finally:
            Migrator.migrations = original_migrations

    def test_run_migration_with_higher_current_version(
        self, mocker: MockerFixture
    ) -> None:
        """Test that migration runs when current version is higher than
        migration version."""
        mocker.patch("svs_core.migrations.migrator.version", return_value="1.0.0")

        mock_migration_func = Mock()
        test_migrations = [
            Migration("test-migration", PackageVersion("0.15.0"), mock_migration_func),
        ]

        original_migrations = Migrator.migrations
        try:
            Migrator.migrations = test_migrations
            Migrator.run(PackageVersion("0.10.0"))

            mock_migration_func.assert_called_once()
        finally:
            Migrator.migrations = original_migrations

    def test_run_multiple_migrations_in_order(self, mocker: MockerFixture) -> None:
        """Test that multiple migrations are executed in order."""
        mocker.patch("svs_core.migrations.migrator.version", return_value="1.0.0")

        mock_migration_func_1 = Mock()
        mock_migration_func_2 = Mock()
        test_migrations = [
            Migration("migration-1", PackageVersion("0.14.0"), mock_migration_func_1),
            Migration("migration-2", PackageVersion("0.15.0"), mock_migration_func_2),
        ]

        original_migrations = Migrator.migrations
        try:
            Migrator.migrations = test_migrations
            Migrator.run(PackageVersion("0.10.0"))

            mock_migration_func_1.assert_called_once()
            mock_migration_func_2.assert_called_once()
        finally:
            Migrator.migrations = original_migrations

    def test_run_skips_already_run_migrations(self, mocker: MockerFixture) -> None:
        """Test that migrations already run (last_known_version >= migration
        version) are skipped."""
        mocker.patch("svs_core.migrations.migrator.version", return_value="1.0.0")

        mock_migration_func_1 = Mock()
        mock_migration_func_2 = Mock()
        test_migrations = [
            Migration("migration-1", PackageVersion("0.14.0"), mock_migration_func_1),
            Migration("migration-2", PackageVersion("0.15.0"), mock_migration_func_2),
        ]

        original_migrations = Migrator.migrations
        try:
            Migrator.migrations = test_migrations
            Migrator.run(PackageVersion("0.14.0"))

            mock_migration_func_1.assert_not_called()
            mock_migration_func_2.assert_called_once()
        finally:
            Migrator.migrations = original_migrations

    def test_restart_policy_change_migration(self, mocker: MockerFixture) -> None:
        """Test that _restart_policy_change recreates all services."""
        mock_service_class = mocker.patch("svs_core.migrations.migrator.Service")
        mock_service_1 = Mock()
        mock_service_2 = Mock()
        mock_service_class.objects.all.return_value = [mock_service_1, mock_service_2]

        Migrator._restart_policy_change()

        mock_service_1.recreate.assert_called_once()
        mock_service_2.recreate.assert_called_once()
