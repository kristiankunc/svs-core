from dataclasses import dataclass
from typing import Optional


@dataclass
class GitHubRepo:
    """Represents a GitHub repository with its owner and name.

    Attributes:
        owner (str): The owner of the repository.
        name (str): The name of the repository.
    """

    owner: str
    name: str
    path: Optional[str] = None


def destruct_github_url(url: str) -> GitHubRepo:
    """Destructs a GitHub URL into owner and repository name.

    Args:
        url (str): The GitHub URL to destruct.

    Returns:
        GitHubRepo: An instance containing the owner and repository name.

    Raises:
        ValueError: If the URL is invalid.
    """
    url = url.strip().rstrip("/")
    if not url.startswith("https://github.com/"):
        raise ValueError("URL must start with 'https://github.com/'")

    url = url[len("https://github.com/") :]
    parts = url.split("/")
    if len(parts) >= 2:
        owner, name = parts[0], parts[1]
        path = "/".join(parts[2:]) if len(parts) > 2 else None
        return GitHubRepo(owner=owner, name=name, path=path)

    raise ValueError("URL must contain at least an owner and a repository name")
