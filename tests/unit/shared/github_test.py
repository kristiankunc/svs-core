import pytest

from svs_core.shared.github import GitHubRepo, destruct_github_url


class TestDestructGitHubUrl:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        "url,expected",
        [
            (
                "https://github.com/owner/repo",
                GitHubRepo(owner="owner", name="repo", path=None),
            ),
            (
                "https://github.com/owner/repo/",
                GitHubRepo(owner="owner", name="repo", path=None),
            ),
            (
                "https://github.com/owner/repo/some/path",
                GitHubRepo(owner="owner", name="repo", path="some/path"),
            ),
            (
                "https://github.com/owner/repo/some/path/",
                GitHubRepo(owner="owner", name="repo", path="some/path"),
            ),
        ],
    )
    def test_valid_urls(self, url, expected):
        result = destruct_github_url(url)
        assert result == expected

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "url",
        [
            "http://github.com/owner/repo",  # wrong protocol
            "https://github.com/owner",  # missing repo
            "https://gitlab.com/owner/repo",  # wrong domain
            "https://github.com/",  # missing owner and repo
            "",  # empty string
        ],
    )
    def test_invalid_urls(self, url):
        with pytest.raises(ValueError):
            destruct_github_url(url)
