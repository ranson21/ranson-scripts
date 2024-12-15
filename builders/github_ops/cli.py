# cli.py

import os
import argparse
from github_ops import GitHubOps


def main():
    parser = argparse.ArgumentParser(description="GitHub Operations CLI")
    parser.add_argument(
        "--action",
        required=True,
        choices=["get-version", "bump-version", "create-release", "update-submodule"],
        help="Action to perform",
    )
    parser.add_argument("--github-token", required=True, help="GitHub token")
    parser.add_argument("--repo-owner", required=True, help="Repository owner")
    parser.add_argument("--repo-name", required=True, help="Repository name")
    parser.add_argument("--pr-number", type=int, help="PR number")
    parser.add_argument("--version-type", help="Version bump type")
    parser.add_argument("--current-version", help="Current version")
    parser.add_argument("--is-draft", action="store_true", help="Create draft release")
    parser.add_argument("--parent-repo", help="Parent repository name")
    parser.add_argument("--submodule-path", help="Submodule path")

    args = parser.parse_args()

    ops = GitHubOps(args.github_token, args.repo_owner, args.repo_name)

    if args.action == "get-version":
        print(ops.get_latest_version())

    elif args.action == "bump-version":
        if not args.current_version or not args.version_type:
            raise ValueError(
                "current-version and version-type are required for bump-version"
            )
        print(ops.bump_version(args.current_version, args.version_type))

    elif args.action == "create-release":
        if not args.current_version:
            raise ValueError("current-version is required for create-release")
        release_id = ops.create_release(args.current_version, args.is_draft)
        print(release_id)

    elif args.action == "update-submodule":
        if not all([args.parent_repo, args.submodule_path, args.current_version]):
            raise ValueError(
                "parent-repo, submodule-path, and current-version are required for update-submodule"
            )
        pr_number = ops.update_submodule(
            args.parent_repo, args.submodule_path, args.current_version
        )
        print(pr_number)


if __name__ == "__main__":
    main()
