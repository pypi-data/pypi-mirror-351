# GitHub REST API

### Usage

Set up python package dependencies in `pyproject.toml`:
```shell
uv sync
```

After sync the project, activate virtualenv in `.venv` directory:
```shell
source .venv/bin/activate
```

To list all installed packages, run:
```shell
uv pip list
```

Export your **GitHub PAT** as environment variable:
```shell
export GITHUB_AUTH_TOKEN="<github-auth-token>"
```

Run cli:
```shell
github-rest-cli -h
```

### Dynaconf

This python cli app uses dynaconf to manage secrets and environment variables.

So that you can use your secrets and environment variables declared in `settings.toml` or `.settings.toml`, use the `GITHUB` prefix value of `envvar_prefix` declared in config.py.

List all defined parameters:
```shell
just dl
```

Validate all defined parameters:
```shell
just dv
```

**NOTE:** To run dynaconf validate `dynaconf_validators.toml` should exist.

### Ruff

Run lint:
```shell
just lint
```

Run format:
```shell
just fmt
```
