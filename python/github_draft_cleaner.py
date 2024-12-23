import requests
import os
import argparse
from typing import List, Dict


class GitHubDraftCleaner:
    def __init__(self, token: str):
        """
        Initialize the cleaner with a GitHub token.

        Args:
            token (str): GitHub personal access token
        """
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
        }
        self.base_url = "https://api.github.com"

    def get_draft_releases(self, owner: str, repo: str) -> List[Dict]:
        """
        Fetch all draft releases from a repository.

        Args:
            owner (str): Repository owner
            repo (str): Repository name

        Returns:
            List[Dict]: List of draft releases
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/releases"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        releases = response.json()
        return [release for release in releases if release["draft"]]

    def delete_release(self, owner: str, repo: str, release_id: int) -> None:
        """
        Delete a specific release.

        Args:
            owner (str): Repository owner
            repo (str): Repository name
            release_id (int): Release ID to delete
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/releases/{release_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()

    def clean_draft_releases(
        self, owner: str, repo: str, dry_run: bool = False
    ) -> None:
        """
        Clean all draft releases from a repository.

        Args:
            owner (str): Repository owner
            repo (str): Repository name
            dry_run (bool): If True, only print what would be deleted without actually deleting
        """
        draft_releases = self.get_draft_releases(owner, repo)

        if not draft_releases:
            print(f"No draft releases found in {owner}/{repo}")
            return

        print(f"Found {len(draft_releases)} draft release(s) in {owner}/{repo}")

        for release in draft_releases:
            if dry_run:
                print(
                    f"Would delete draft release: {release['name']} (ID: {release['id']})"
                )
            else:
                print(
                    f"Deleting draft release: {release['name']} (ID: {release['id']})"
                )
                self.delete_release(owner, repo, release["id"])

        if not dry_run:
            print(f"Successfully deleted {len(draft_releases)} draft release(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Clean draft releases from a GitHub repository"
    )
    parser.add_argument("owner", help="Repository owner")
    parser.add_argument("repo", help="Repository name")
    parser.add_argument(
        "--token",
        help="GitHub token (or set GITHUB_TOKEN env var)",
        default=os.environ.get("GITHUB_TOKEN"),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be deleted without actually deleting",
    )

    args = parser.parse_args()

    if not args.token:
        raise ValueError(
            "GitHub token must be provided via --token or GITHUB_TOKEN environment variable"
        )

    cleaner = GitHubDraftCleaner(args.token)

    try:
        cleaner.clean_draft_releases(args.owner, args.repo, args.dry_run)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
