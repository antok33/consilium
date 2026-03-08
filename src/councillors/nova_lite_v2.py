"""
Amazon Nova Lite v2 Councillor
"""
from dotenv import load_dotenv
from .base import Councillor

load_dotenv()


class NovaLiteV2Councillor(Councillor):
    """Amazon Nova Lite v2 - Lightweight model."""

    def __init__(self):
        super().__init__(
            name="Amazon Nova Lite v2",
            model_id="global.amazon.nova-2-lite-v1:0",
            region_name="us-east-1"
        )


# Create a singleton instance for easy import
nova_lite_councillor = NovaLiteV2Councillor()
