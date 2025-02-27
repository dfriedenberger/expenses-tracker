import os


# Retrieving an environment variable with error handling
def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        raise RuntimeError(f"Fehlende Umgebungsvariable: {var_name}")
    return value
