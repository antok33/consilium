"""
Meta Llama 3.3 70B Councillor
"""
from dotenv import load_dotenv
from .base import Councillor

load_dotenv()


class Llama33Councillor(Councillor):
    """Meta Llama 3.3 70B Instruct."""

    def __init__(self):
        super().__init__(
            name="Llama 3.3 70B",
            model_id="us.meta.llama3-3-70b-instruct-v1:0",
            region_name="us-east-1"
        )


# Create a singleton instance for easy import
llama_councillor = Llama33Councillor()
