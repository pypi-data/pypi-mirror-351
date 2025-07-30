from nonebot import require

require("nonebot_plugin_htmlrender")
# pylint: disable=wrong-import-position
import nonebot_plugin_htmlrender as htmlrender


async def html_to_pic(html: str) -> bytes:
    """
    Converts the given text into an image using the htmlrender plugin.

    Args:
        text (str): The HTML content to be rendered into an image.

    Returns:
        The generated image in bytes format.
        type: bytes
    """
    return await htmlrender.html_to_pic(
        html=html,
        screenshot_timeout=10000,
        viewport={'width': 300, 'height': 10}
    )

async def md_to_pic(md_text: str) -> bytes:
    """
    Converts the given markdown text into an image using the htmlrender plugin.

    Args:
        md_text (str): The markdown content to be rendered into an image.

    Returns:
        The generated image in bytes format.
        type: bytes
    """
    return await htmlrender.md_to_pic(
        md_text
    )
