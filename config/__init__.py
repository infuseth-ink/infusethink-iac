"""Configuration loader for environment-specific settings."""

from typing import Any

import pulumi


def load_config() -> dict[str, Any]:
    """Load configuration based on the current Pulumi stack.

    Returns:
        Configuration dictionary for the current environment
    """
    stack = pulumi.get_stack()

    if stack == "dev":
        from .dev import get_config

        return get_config()
    else:
        msg = f"Unknown stack: {stack}. Currently only 'dev' stack is supported."
        raise ValueError(msg)
