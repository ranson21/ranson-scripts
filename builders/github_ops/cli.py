import os
import argparse
from github_ops import GitHubOps


def write_version_to_file(version: str, filename: str) -> None:
    """Write version string to a file"""
    with open(filename, "w") as f:
        f.write(version)


def str2bool(v):
    """Convert string to boolean value"""
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def main():
    parser = argparse.ArgumentParser(description="GitHub Operations CLI")
    parser.add_argument(
        "--action",
        required=True,
        choices=["get-version", "bump-version", "create-release", "update-submodule"],
        help="Action to perform",
    )
    # Make github-token optional since we'll check environment variable
    parser.add_argument("--github-token", help="GitHub token")
    parser.add_argument("--repo-owner", required=True, help="Repository owner")
    parser.add_argument("--repo-name", required=True, help="Repository name")
    parser.add_argument("--pr-number", type=int, help="PR number")
    parser.add_argument("--version-type", help="Version bump type")
    parser.add_argument("--current-version", help="Current version")
    parser.add_argument("--is-draft", action="store_true", help="Create draft release")
    parser.add_argument("--parent-repo", help="Parent repository name")
    parser.add_argument("--submodule-path", help="Submodule path")
    parser.add_argument(
        "--is-merge",
        type=str2bool,
        default=False,
        help="Whether this is a merge operation",
    )

    args = parser.parse_args()

    # Get token from args or environment
    github_token = args.github_token or os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "GitHub token must be provided either via --github-token or GITHUB_TOKEN environment variable"
        )

    ops = GitHubOps(github_token, args.repo_owner, args.repo_name)

    if args.action == "get-version":
        version = ops.get_latest_version()
        write_version_to_file(version, "current_version.txt")
        print(f"Latest version {version} written to current_version.txt")

    elif args.action == "bump-version":
        if not args.current_version or not args.version_type:
            raise ValueError(
                "current-version and version-type are required for bump-version"
            )
        new_version = ops.bump_version(args.current_version, args.version_type)
        write_version_to_file(new_version, "new_version.txt")
        print(f"New version {new_version} written to new_version.txt")

    elif args.action == "create-release":
        if not args.current_version:
            raise ValueError("current-version is required for create-release")
        release_id = ops.create_release(args.current_version, args.is_draft)
        print(f"Created release with ID: {release_id}")

    elif args.action == "update-submodule":
        if not args.is_merge:
            print("Skipping submodule update as this is not a merge operation")
            return

        if not all([args.parent_repo, args.submodule_path, args.current_version]):
            raise ValueError(
                "parent-repo, submodule-path, and current-version are required for update-submodule"
            )
        pr_number = ops.update_submodule(
            args.parent_repo, args.submodule_path, args.current_version
        )
        print(f"Created PR #{pr_number} for submodule update")


if __name__ == "__main__":
    main()
