from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    # Default environment variables prefix.
    envvar_prefix="GITHUB",
    # Source configuration files.
    settings_files=["../../settings.toml", "../../.secrets.toml"],
    environments=["development", "testing", "production"],
    env_switcher="SET_ENV",
    # The script will not work if the variables
    # defined in the Validator class are not defined.
    validators=[
        Validator(
            "AUTH_TOKEN",
            must_exist=True,
            messages={
                "must_exist_true": "Environment variable GITHUB_AUTH_TOKEN is not set. Please set it and try again."
            },
        ),
    ],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
