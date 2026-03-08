"""
Amazon Nova Premier Councillor
"""
from dotenv import load_dotenv
from .base import Councillor

load_dotenv()


class NovaPremierCouncillor(Councillor):
    """Amazon Nova Premier - Amazon's most capable multimodal model."""

    def __init__(self):
        super().__init__(
            name="Amazon Nova Premier",
            model_id="us.amazon.nova-premier-v1:0",
            region_name="us-east-1"
        )


# Create a singleton instance for easy import
nova_premier_councillor = NovaPremierCouncillor()
