"""
Base class for all councillors in the Multi-Agent Debate system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from langchain_aws import ChatBedrockConverse


class Councillor(ABC):
    """
    Abstract base class for councillors.

    Each councillor represents a different LLM model that participates
    in the multi-agent debate process.
    """

    def __init__(self, name: str, model_id: str, region_name: str = "us-east-1"):
        """
        Initialize a councillor.

        Args:
            name: Human-readable name for this councillor
            model_id: AWS Bedrock model ID
            region_name: AWS region for Bedrock
        """
        self.name = name
        self.model_id = model_id
        self.region_name = region_name
        self._llm = None

    @property
    def llm(self) -> ChatBedrockConverse:
        """
        Lazy-load the LLM instance.

        Returns:
            Initialized ChatBedrockConverse instance
        """
        if self._llm is None:
            self._llm = ChatBedrockConverse(
                model_id=self.model_id,
                region_name=self.region_name,
            )
        return self._llm

    def invoke(self, prompt: str) -> str:
        """
        Invoke the councillor with a prompt and return the response.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The LLM's response as a string
        """
        try:
            response = self.llm.invoke(prompt)

            # Handle different response formats
            if hasattr(response, 'content'):
                return response.content
            elif hasattr(response, 'content_blocks') and len(response.content_blocks) > 0:
                return response.content_blocks[0].get("text", str(response))
            else:
                return str(response)

        except Exception as e:
            return f"Error invoking {self.name}: {str(e)}"

    def __str__(self) -> str:
        return f"{self.name} ({self.model_id})"

    def __repr__(self) -> str:
        return f"Councillor(name='{self.name}', model_id='{self.model_id}')"
