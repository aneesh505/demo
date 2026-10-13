import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

def create_pull_request(repo_url: str, branch_name: str, title: str, body: str) -> str:
    """
    Creates a pull request using the Fork & PR workflow.
    1. Extracts owner/repo from repo_url.
    2. Forks the repo to the authenticated user's account if needed.
    3. Creates a pull request from the user's fork/branch to the upstream repository.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("GitHub token not configured. Skipping PR creation.")
        return "https://github.com/mock-pr-url"

    g = Github(token)
    user = g.get_user()

    # Extract owner/repo from repo_url (e.g. https://github.com/owner/repo)
    clean_url = repo_url.rstrip(".git").rstrip("/")
    parts = clean_url.replace("https://github.com/", "").split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid repository URL: {repo_url}")

    owner, repo_name = parts[0], parts[1]
    upstream_full_name = f"{owner}/{repo_name}"

    try:
        upstream_repo = g.get_repo(upstream_full_name)
    except Exception as e:
        print(f"Error accessing upstream repository {upstream_full_name}: {e}")
        return ""

    # 1. Automatically fork repository to authenticated user's account
    try:
        print(f"Forking {upstream_full_name} to user account ({user.login})...")
        my_fork = user.create_fork(upstream_repo)
    except Exception as e:
        print(f"Fork may already exist or encountered note: {e}")
        my_fork = g.get_repo(f"{user.login}/{repo_name}")

    # 2. Create Pull Request from user's fork to upstream repo
    try:
        print(f"Creating Pull Request on {upstream_full_name} from {user.login}:{branch_name}...")
        pr = upstream_repo.create_pull(
            title=title,
            body=body,
            head=f"{user.login}:{branch_name}",
            base=upstream_repo.default_branch
        )
        print(f"Pull Request successfully created: {pr.html_url}")
        return pr.html_url
    except Exception as e:
        print(f"Error creating pull request (ensure branch {branch_name} is pushed to your fork): {e}")
        return ""

if __name__ == "__main__":
    # Test stub
    print("pr.py module loaded successfully.")
