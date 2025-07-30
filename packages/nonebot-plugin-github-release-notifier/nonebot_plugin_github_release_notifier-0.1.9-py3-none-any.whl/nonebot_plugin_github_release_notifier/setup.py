# pylint: disable=missing-module-docstring
from .repo_activity import validate_github_token

async def post_plugin_setup() -> None:
    """Post plugin setup function to validate GitHub token."""
    await validate_github_token()
