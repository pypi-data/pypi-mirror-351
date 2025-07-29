import argparse
from github_rest_cli.api import (
    fetch_user,
    get_repository,
    create_repository,
    delete_repository,
    list_repositories,
    dependabot_security,
    deployment_environment,
)


def cli():
    """
    Create parsers and subparsers for CLI arguments
    """
    global_parser = argparse.ArgumentParser(
        description="Python CLI to GitHub REST API",
    )
    subparsers = global_parser.add_subparsers(
        help="Python GitHub REST API commands", dest="command"
    )

    # Subparser for "get-repository" function
    get_repo_parser = subparsers.add_parser(
        "get-repo", help="Get repository information"
    )
    get_repo_parser.add_argument(
        "-n",
        "--name",
        help="The repository name",
        required=True,
        dest="name",
    )
    get_repo_parser.add_argument(
        "-o", "--org", help="The organization name", required=False, dest="org"
    )

    # Subparser for "list-repository" function
    list_repo_parser = subparsers.add_parser(
        "list-repo",
        help="List repositories for authenticated user",
    )
    list_repo_parser.add_argument(
        "-r",
        "--role",
        required=False,
        dest="role",
        help="List repositories by role",
    )
    list_repo_parser.add_argument(
        "-p",
        "--page",
        required=False,
        default=50,
        type=int,
        dest="page",
        help="The number of results",
    )
    list_repo_parser.add_argument(
        "-s",
        "--sort",
        required=False,
        default="pushed",
        dest="sort",
        help="List repositories sorted by",
    )

    # Subparser for "create-repository" function
    create_repo_parser = subparsers.add_parser(
        "create-repo",
        help="Create a new repository",
    )
    create_repo_parser.add_argument(
        "-n",
        "--name",
        required=True,
        dest="name",
        help="The repository name",
    )
    create_repo_parser.add_argument(
        "-v",
        "--visibility",
        required=False,
        default="public",
        dest="visibility",
        help="Whether the repository is private",
    )
    create_repo_parser.add_argument(
        "-o",
        "--org",
        required=False,
        dest="org",
        help="The organization name",
    )

    # Subparser for "delete-repository" function
    delete_repo_parser = subparsers.add_parser(
        "delete-repo",
        help="Delete a repository",
    )
    delete_repo_parser.add_argument(
        "-n",
        "--name",
        required=True,
        dest="name",
        help="The repository name",
    )
    delete_repo_parser.add_argument(
        "-o",
        "--org",
        required=False,
        dest="org",
        help="The organization name",
    )

    # Subparser for "dependabot" function
    dependabot_parser = subparsers.add_parser(
        "dependabot",
        help="Github Dependabot security updates",
    )
    dependabot_parser.add_argument(
        "-n",
        "--name",
        required=True,
        dest="name",
        help="The repository name",
    )
    dependabot_parser.add_argument(
        "-o",
        "--org",
        dest="org",
        help="The organization name",
    )
    dependabot_parser.add_argument(
        "--enable",
        required=False,
        action="store_true",
        dest="control",
        help="Enable dependabot security updates",
    )
    dependabot_parser.add_argument(
        "--disable",
        required=False,
        action="store_false",
        dest="control",
        help="Disable dependabot security updates",
    )

    # Subparser for "deployment-environments" function
    deploy_env_parser = subparsers.add_parser(
        "environment",
        help="Github Deployment environments",
    )
    deploy_env_parser.add_argument(
        "-n",
        "--name",
        required=True,
        dest="name",
        help="The repository name",
    )
    deploy_env_parser.add_argument(
        "-e",
        "--env",
        required=True,
        dest="env",
        help="Deployment environment name",
    )
    deploy_env_parser.add_argument(
        "-o",
        "--org",
        required=False,
        dest="org",
        help="The organization name",
    )

    # guard clause pattern
    args = global_parser.parse_args()
    command = args.command

    owner = fetch_user()

    if command == "get-repo":
        return get_repository(owner, args.name, args.org)
    if command == "list-repo":
        return list_repositories(args.page, args.sort, args.role)
    if command == "create-repo":
        return create_repository(owner, args.name, args.visibility, args.org)
    if command == "delete-repo":
        return delete_repository(owner, args.name, args.org)
    if command == "dependabot":
        return dependabot_security(owner, args.name, args.control, args.org)
    if command == "environment":
        return deployment_environment(owner, args.name, args.env, args.org)
    return False


if __name__ == "__main__":
    cli()
