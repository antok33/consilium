"""
Amazon Nova Pro Councillor
"""
from dotenv import load_dotenv
from .base import Councillor

load_dotenv()


class NovaProCouncillor(Councillor):
    """Amazon Nova Pro."""

    def __init__(self):
        super().__init__(
            name="Amazon Nova Pro",
            model_id="us.amazon.nova-pro-v1:0",
            region_name="us-east-1"
        )


# Create a singleton instance for easy import
nova_pro_councillor = NovaProCouncillor()
