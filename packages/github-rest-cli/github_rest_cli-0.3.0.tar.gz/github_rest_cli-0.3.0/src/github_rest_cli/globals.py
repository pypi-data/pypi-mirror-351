from github_rest_cli.config import settings

GITHUB_URL = "https://api.github.com"
GITHUB_TOKEN = f"{settings.AUTH_TOKEN}"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Authorization": f"token {GITHUB_TOKEN}",
}
