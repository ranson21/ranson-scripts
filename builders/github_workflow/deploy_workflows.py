import os
from github import Github
import base64

# Initialize GitHub client with your PAT
g = Github(os.environ.get("GITHUB_TOKEN"))


# Read repositories from file
def read_repo_list(filename="repos.txt"):
    with open(filename, "r") as f:
        # Strip whitespace and empty lines
        return [line.strip() for line in f if line.strip()]


# The workflow content
workflow_content = """name: Check Required Labels

on:
  pull_request:
    types: [opened, labeled, unlabeled, synchronize]

# Add permissions block
permissions:
  checks: write
  pull-requests: read

jobs:
  check-labels:
    runs-on: ubuntu-latest
    steps:
      - name: Check for required labels
        uses: actions/github-script@v7
        with:
          script: |
            const requiredLabels = ['semver:major', 'semver:minor', 'semver:patch'];
            const prLabels = context.payload.pull_request.labels.map(label => label.name);
            
            const hasRequiredLabel = requiredLabels.some(label => prLabels.includes(label));
            
            if (!hasRequiredLabel) {
              core.setFailed('PR must have one of the following labels: ' + requiredLabels.join(', '));
            }

      - name: Update Check Run
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const requiredLabels = ['semver:major', 'semver:minor', 'semver:patch'];
            const prLabels = context.payload.pull_request.labels.map(label => label.name);
            const hasRequiredLabel = requiredLabels.some(label => prLabels.includes(label));
            
            const conclusion = hasRequiredLabel ? 'success' : 'failure';
            const title = hasRequiredLabel ? 'Required label present' : 'Missing required label';
            const summary = hasRequiredLabel 
              ? 'PR has one of the required semver labels'
              : 'PR must have one of the following labels: ' + requiredLabels.join(', ');
            
            await github.rest.checks.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              name: 'Label Check',
              head_sha: context.payload.pull_request.head.sha,
              status: 'completed',
              conclusion: conclusion,
              output: {
                title: title,
                summary: summary
              }
            });
"""


def ensure_workflow_directory(repo):
    """Ensure .github/workflows directory exists"""
    try:
        repo.get_contents(".github/workflows")
    except:
        repo.create_file(
            ".github/workflows/.gitkeep",
            "Create workflows directory",
            "",
            branch="master",  # Using 'main' as default branch
        )


def create_or_update_workflow(repo, path, content):
    """Create or update workflow file, always recreating it"""
    try:
        # Check if file exists and delete it
        try:
            contents = repo.get_contents(path)
            repo.delete_file(
                path, "Remove existing workflow for recreation", contents.sha
            )
            print(f"Deleted existing workflow in {repo.name}")
        except:
            pass  # File doesn't exist, continue to creation

        # Create new file
        repo.create_file(path, "Add label check workflow", content)
        print(f"Created workflow in {repo.name}")

    except Exception as e:
        print(f"Error in {repo.name}: {str(e)}")


def main():
    # Get list of target repositories
    target_repos = read_repo_list()

    # Get the authenticated user
    user = g.get_user()

    # Process each repository
    for repo_name in target_repos:
        try:
            # Get repository object
            repo = g.get_repo(f"{user.login}/{repo_name}")

            # Skip if it's a fork (optional - you can remove this check)
            if repo.fork:
                print(f"Skipping fork: {repo.name}")
                continue

            # Ensure workflows directory exists
            ensure_workflow_directory(repo)

            # Create or update workflow file
            path = ".github/workflows/check-labels.yml"
            create_or_update_workflow(repo, path, workflow_content)

        except Exception as e:
            print(f"Error processing {repo_name}: {str(e)}")


if __name__ == "__main__":
    main()
