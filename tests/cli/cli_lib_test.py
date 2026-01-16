import pytest

from pytest_mock import MockerFixture

from svs_core.cli.lib import (
    git_source_id_autocomplete,
    service_id_autocomplete,
    template_id_autocomplete,
    username_autocomplete,
)


@pytest.mark.cli
class TestAutocompletion:
    """Tests for CLI autocompletion functions."""

    @pytest.fixture(autouse=True)
    def reset_context(self):
        """Reset context variables before each test."""
        from svs_core.cli.state import current_user

        current_user.set(None)

    # username_autocomplete tests
    def test_username_autocomplete_as_admin(self, mocker: MockerFixture) -> None:
        """Test username autocomplete returns all matching users for admin."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=True)

        mock_user1 = mocker.MagicMock()
        mock_user1.name = "alice"
        mock_user2 = mocker.MagicMock()
        mock_user2.name = "alison"

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.return_value = [mock_user1, mock_user2]

        mock_user_model = mocker.patch("svs_core.users.user.User")
        mock_user_model.objects = mock_queryset

        result = username_autocomplete("ali")

        assert len(result) == 2
        assert result[0] == ("alice", "alice")
        assert result[1] == ("alison", "alison")
        mock_queryset.filter.assert_called_once_with(name__startswith="ali")

    def test_username_autocomplete_as_regular_user(self, mocker: MockerFixture) -> None:
        """Test username autocomplete for non-admin users filters to their own
        username.

        Non-admin users can only autocomplete their own username, so the
        filter checks both that name equals current user AND name starts
        with the incomplete string.
        """
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=False)
        mocker.patch("svs_core.cli.lib.get_current_username", return_value="bob")

        mock_user = mocker.MagicMock()
        mock_user.name = "bob"

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.return_value = [mock_user]

        mock_user_model = mocker.patch("svs_core.users.user.User")
        mock_user_model.objects = mock_queryset

        result = username_autocomplete("bo")

        assert len(result) == 1
        assert result[0] == ("bob", "bob")
        # Filter checks both name equals current user AND name starts with incomplete
        mock_queryset.filter.assert_called_once_with(name="bob", name__startswith="bo")

    def test_username_autocomplete_no_current_user(self, mocker: MockerFixture) -> None:
        """Test username autocomplete returns empty list when no current
        user."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=False)
        mocker.patch("svs_core.cli.lib.get_current_username", return_value=None)

        result = username_autocomplete("test")

        assert result == []

    def test_username_autocomplete_exception_handling(
        self, mocker: MockerFixture
    ) -> None:
        """Test username autocomplete handles exceptions gracefully."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=True)

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.side_effect = Exception("Database error")

        mock_user_model = mocker.patch("svs_core.users.user.User")
        mock_user_model.objects = mock_queryset

        result = username_autocomplete("test")

        assert result == []

    # service_id_autocomplete tests
    def test_service_id_autocomplete_as_admin(self, mocker: MockerFixture) -> None:
        """Test service ID autocomplete returns all matching services for
        admin."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=True)

        mock_service1 = mocker.MagicMock()
        mock_service1.id = "nginx-1"
        mock_service1.name = "nginx-1"
        mock_service2 = mocker.MagicMock()
        mock_service2.id = "nginx-2"
        mock_service2.name = "nginx-2"

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.return_value = [mock_service1, mock_service2]

        mock_service_model = mocker.patch("svs_core.docker.service.Service")
        mock_service_model.objects = mock_queryset

        result = service_id_autocomplete("ngin")

        assert len(result) == 2
        assert result[0] == ("nginx-1", "nginx-1")
        assert result[1] == ("nginx-2", "nginx-2")
        mock_queryset.filter.assert_called_once_with(id__startswith="ngin")

    def test_service_id_autocomplete_as_regular_user(
        self, mocker: MockerFixture
    ) -> None:
        """Test service ID autocomplete returns only user's services for non-
        admin."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=False)
        mocker.patch("svs_core.cli.lib.get_current_username", return_value="alice")

        mock_service = mocker.MagicMock()
        mock_service.id = "my-service"
        mock_service.name = "my-service"

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.return_value = [mock_service]

        mock_service_model = mocker.patch("svs_core.docker.service.Service")
        mock_service_model.objects = mock_queryset

        result = service_id_autocomplete("my")

        assert len(result) == 1
        assert result[0] == ("my-service", "my-service")
        mock_queryset.filter.assert_called_once_with(
            user__name="alice", id__startswith="my"
        )

    def test_service_id_autocomplete_no_current_user(
        self, mocker: MockerFixture
    ) -> None:
        """Test service ID autocomplete returns empty list when no current
        user."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=False)
        mocker.patch("svs_core.cli.lib.get_current_username", return_value=None)

        result = service_id_autocomplete("test")

        assert result == []

    def test_service_id_autocomplete_exception_handling(
        self, mocker: MockerFixture
    ) -> None:
        """Test service ID autocomplete handles exceptions gracefully."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=True)

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.side_effect = Exception("Database error")

        mock_service_model = mocker.patch("svs_core.docker.service.Service")
        mock_service_model.objects = mock_queryset

        result = service_id_autocomplete("test")

        assert result == []

    # template_id_autocomplete tests
    def test_template_id_autocomplete_as_admin(self, mocker: MockerFixture) -> None:
        """Test template ID autocomplete returns all matching templates for
        admin."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=True)

        mock_template1 = mocker.MagicMock()
        mock_template1.id = "django"
        mock_template1.name = "django"
        mock_template2 = mocker.MagicMock()
        mock_template2.id = "django-advanced"
        mock_template2.name = "django-advanced"

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.return_value = [mock_template1, mock_template2]

        mock_template_model = mocker.patch("svs_core.docker.template.Template")
        mock_template_model.objects = mock_queryset

        result = template_id_autocomplete("django")

        assert len(result) == 2
        assert result[0] == ("django", "django")
        assert result[1] == ("django-advanced", "django-advanced")
        mock_queryset.filter.assert_called_once_with(id__startswith="django")

    def test_template_id_autocomplete_as_regular_user(
        self, mocker: MockerFixture
    ) -> None:
        """Test template autocomplete for non-admin users shows all templates.

        Templates use owner_check='' (empty string), which is falsy, so
        the filter falls through to the else branch and only filters by
        id__startswith. This allows all users to see all templates
        regardless of ownership.
        """
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=False)
        mocker.patch("svs_core.cli.lib.get_current_username", return_value="alice")

        mock_template = mocker.MagicMock()
        mock_template.id = "nginx"
        mock_template.name = "nginx"

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.return_value = [mock_template]

        mock_template_model = mocker.patch("svs_core.docker.template.Template")
        mock_template_model.objects = mock_queryset

        result = template_id_autocomplete("ngin")

        assert len(result) == 1
        assert result[0] == ("nginx", "nginx")
        # Empty owner_check means only id__startswith filter is applied
        mock_queryset.filter.assert_called_once_with(id__startswith="ngin")

    def test_template_id_autocomplete_exception_handling(
        self, mocker: MockerFixture
    ) -> None:
        """Test template ID autocomplete handles exceptions gracefully."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=True)

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.side_effect = Exception("Database error")

        mock_template_model = mocker.patch("svs_core.docker.template.Template")
        mock_template_model.objects = mock_queryset

        result = template_id_autocomplete("test")

        assert result == []

    # git_source_id_autocomplete tests
    def test_git_source_id_autocomplete_as_admin(self, mocker: MockerFixture) -> None:
        """Test git source ID autocomplete returns all matching sources for
        admin."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=True)

        mock_source1 = mocker.MagicMock()
        mock_source1.id = "repo-1"
        mock_source1.name = "repo-1"
        mock_source2 = mocker.MagicMock()
        mock_source2.id = "repo-2"
        mock_source2.name = "repo-2"

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.return_value = [mock_source1, mock_source2]

        mock_git_source_model = mocker.patch("svs_core.shared.git_source.GitSource")
        mock_git_source_model.objects = mock_queryset

        result = git_source_id_autocomplete("repo")

        assert len(result) == 2
        assert result[0] == ("repo-1", "repo-1")
        assert result[1] == ("repo-2", "repo-2")
        mock_queryset.filter.assert_called_once_with(id__startswith="repo")

    def test_git_source_id_autocomplete_as_regular_user(
        self, mocker: MockerFixture
    ) -> None:
        """Test git source ID autocomplete returns only user's sources for non-
        admin."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=False)
        mocker.patch("svs_core.cli.lib.get_current_username", return_value="alice")

        mock_source = mocker.MagicMock()
        mock_source.id = "my-repo"
        mock_source.name = "my-repo"

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.return_value = [mock_source]

        mock_git_source_model = mocker.patch("svs_core.shared.git_source.GitSource")
        mock_git_source_model.objects = mock_queryset

        result = git_source_id_autocomplete("my")

        assert len(result) == 1
        assert result[0] == ("my-repo", "my-repo")
        mock_queryset.filter.assert_called_once_with(
            service__user__name="alice", id__startswith="my"
        )

    def test_git_source_id_autocomplete_no_current_user(
        self, mocker: MockerFixture
    ) -> None:
        """Test git source ID autocomplete returns empty list when no current
        user."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=False)
        mocker.patch("svs_core.cli.lib.get_current_username", return_value=None)

        result = git_source_id_autocomplete("test")

        assert result == []

    def test_git_source_id_autocomplete_exception_handling(
        self, mocker: MockerFixture
    ) -> None:
        """Test git source ID autocomplete handles exceptions gracefully."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=True)

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.side_effect = Exception("Database error")

        mock_git_source_model = mocker.patch("svs_core.shared.git_source.GitSource")
        mock_git_source_model.objects = mock_queryset

        result = git_source_id_autocomplete("test")

        assert result == []

    # Edge cases and empty results
    def test_autocomplete_empty_incomplete_string(self, mocker: MockerFixture) -> None:
        """Test autocomplete with empty string returns all items."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=True)

        mock_user1 = mocker.MagicMock()
        mock_user1.name = "alice"
        mock_user2 = mocker.MagicMock()
        mock_user2.name = "bob"

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.return_value = [mock_user1, mock_user2]

        mock_user_model = mocker.patch("svs_core.users.user.User")
        mock_user_model.objects = mock_queryset

        result = username_autocomplete("")

        assert len(result) == 2
        mock_queryset.filter.assert_called_once_with(name__startswith="")

    def test_autocomplete_no_matches(self, mocker: MockerFixture) -> None:
        """Test autocomplete with no matching items returns empty list."""
        mocker.patch("svs_core.cli.lib.is_current_user_admin", return_value=True)

        mock_queryset = mocker.MagicMock()
        mock_queryset.filter.return_value = []

        mock_user_model = mocker.patch("svs_core.users.user.User")
        mock_user_model.objects = mock_queryset

        result = username_autocomplete("nonexistent")

        assert result == []
