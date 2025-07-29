# Justfile for Python

set dotenv-load := true

# Alias

alias dl := dynaconf-list
alias dv := dynaconf-validate

@setup-pre-commit:
    pre-commit install

@setup-ruff:
    uv tool install ruff

test:
    @echo {{ justfile_directory() }}

@cc:
    uv clean cache

@build:
    uv build

@publish:
    uv publish --token $PYPI_TOKEN

@lint:
    ruff check .

@fmt:
    ruff format .

@dynaconf-list:
    dynaconf -i github_rest_cli.config.settings list

@dynaconf-validate:
    dynaconf -i github_rest_cli.config.settings validate
