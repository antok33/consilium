"""
Claude Sonnet 4 Councillor
"""
from dotenv import load_dotenv
from .base import Councillor

load_dotenv()


class ClaudeSonnetV4Councillor(Councillor):
    """Claude Sonnet 4."""

    def __init__(self):
        super().__init__(
            name="Claude Sonnet 4",
            model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
            region_name="us-east-1"
        )


# Create a singleton instance for easy import
claude_sonnet_v4_councillor = ClaudeSonnetV4Councillor()
