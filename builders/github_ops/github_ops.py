# github_ops.py

import os
import re
import json
import subprocess
from datetime import datetime
from typing import Optional, Tuple, Dict
import requests


class GitHubOps:
    def __init__(self, github_token: str, repo_owner: str, repo_name: str):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.api_base = "https://api.github.com"

    def get_latest_version(self) -> str:
        """Get the latest release version from GitHub."""
        url = (
            f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        )
        response = requests.get(url, headers=self.headers)

        if response.status_code == 404:
            return "v0.0.0"

        response.raise_for_status()
        return response.json()["tag_name"]

    def get_pr_info(self, pr_number: int) -> Dict:
        """Get PR information including labels."""
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}?state=all"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def determine_version_type(self, pr_labels: list) -> str:
        """Determine version type based on PR labels."""
        label_mapping = {
            "semver:major": "major",
            "semver:minor": "minor",
            "semver:patch": "patch",
        }

        for label in pr_labels:
            label_name = label["name"]
            if label_name in label_mapping:
                return label_mapping[label_name]

        return "timestamp"

    def bump_version(self, current_version: str, bump_type: str) -> str:
        """Bump version based on type."""
        current = current_version.lstrip("v")

        if bump_type == "timestamp":
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"v{current}-{timestamp}"

        try:
            major, minor, patch = map(int, current.split("."))
        except ValueError:
            return f"v0.0.0-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        if bump_type == "major":
            major += 1
            minor = patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1

        return f"v{major}.{minor}.{patch}"

    def create_release(self, version: str, is_draft: bool = False) -> int:
        """Create a new GitHub release."""
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/releases"
        data = {
            "tag_name": version,
            "name": f"Release {version}",
            "body": f"Release version {version}",
            "draft": is_draft,
            "prerelease": False,
        }

        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()["id"]

    def upload_release_asset(
        self, release_id: int, file_path: str, file_name: str
    ) -> None:
        """Upload an asset to a release."""
        url = f"https://uploads.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/{release_id}/assets"
        params = {"name": file_name}
        headers = {**self.headers, "Content-Type": "application/gzip"}

        with open(file_path, "rb") as f:
            response = requests.post(url, headers=headers, params=params, data=f)
        response.raise_for_status()

    def update_submodule(
        self, parent_repo: str, submodule_path: str, new_version: str
    ) -> str:
        """Update submodule in parent repository and create PR."""
        # Clone parent repo
        subprocess.run(
            [
                "git",
                "clone",
                f"https://oauth2:{self.github_token}@github.com/{self.repo_owner}/{parent_repo}.git",
                "parent-repo",
            ],
            check=True,
        )

        os.chdir("parent-repo")

        # Configure git
        subprocess.run(
            ["git", "config", "user.email", "cloudbuild@example.com"], check=True
        )
        subprocess.run(["git", "config", "user.name", "Cloud Build"], check=True)

        # Update submodule
        subprocess.run(
            ["git", "submodule", "update", "--init", submodule_path], check=True
        )

        # Create branch and update submodule
        branch_name = f"update-{self.repo_name}-{new_version}"
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)

        os.chdir(submodule_path)
        old_commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        )
        subprocess.run(["git", "fetch", "origin"], check=True)
        subprocess.run(["git", "checkout", "master"], check=True)
        subprocess.run(["git", "pull"], check=True)
        new_commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        )

        os.chdir("../..")
        subprocess.run(["git", "add", submodule_path], check=True)
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"chore: update {self.repo_name} submodule to {new_version}",
            ],
            check=True,
        )
        subprocess.run(["git", "push", "origin", branch_name], check=True)

        return self.create_submodule_pr(
            parent_repo, branch_name, new_version, old_commit, new_commit
        )

    def create_submodule_pr(
        self,
        parent_repo: str,
        branch_name: str,
        version: str,
        old_commit: str,
        new_commit: str,
    ) -> str:
        """Create PR for submodule update."""
        url = f"{self.api_base}/repos/{self.repo_owner}/{parent_repo}/pulls"
        data = {
            "title": f"Update {self.repo_name} submodule to {version}",
            "body": f"This PR updates the {self.repo_name} submodule from commit `{old_commit}` to `{new_commit}`\n\nVersion: {version}",
            "head": branch_name,
            "base": "master",
        }

        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()["number"]
