"""
Unit tests for Councillor classes.
"""
import pytest
from councillors.base import Councillor
from councillors import (
    NovaPremierCouncillor,
    ClaudeSonnetV4Councillor,
    NovaProCouncillor,
    NovaLiteV2Councillor,
    Llama33Councillor,
    nova_premier_councillor,
    claude_sonnet_v4_councillor,
    nova_pro_councillor,
    nova_lite_councillor,
    llama_councillor,
)


class TestBaseCouncillor:
    """Tests for the base Councillor class."""

    def test_councillor_initialization(self):
        """Test that a councillor can be initialized."""
        councillor = NovaPremierCouncillor()
        assert councillor.name == "Amazon Nova Premier"
        assert "nova-premier" in councillor.model_id.lower()
        assert councillor.region_name == "us-east-1"

    def test_councillor_lazy_loading(self):
        """Test that LLM is lazy-loaded."""
        councillor = NovaPremierCouncillor()
        assert councillor._llm is None
        # Accessing llm property should trigger loading
        llm = councillor.llm
        assert llm is not None
        assert councillor._llm is not None

    def test_councillor_string_representation(self):
        """Test string representation of councillor."""
        councillor = NovaPremierCouncillor()
        str_repr = str(councillor)
        assert "Amazon Nova Premier" in str_repr
        assert "nova-premier" in str_repr.lower()

    def test_councillor_repr(self):
        """Test repr of councillor."""
        councillor = NovaPremierCouncillor()
        repr_str = repr(councillor)
        assert "Councillor" in repr_str
        assert "Amazon Nova Premier" in repr_str


class TestIndividualCouncillors:
    """Tests for individual councillor implementations."""

    def test_nova_premier_councillor(self):
        """Test Nova Premier councillor."""
        assert nova_premier_councillor.name == "Amazon Nova Premier"
        assert "nova-premier" in nova_premier_councillor.model_id.lower()

    def test_claude_sonnet_v4_councillor(self):
        """Test Claude Sonnet 4 councillor."""
        assert "Sonnet" in claude_sonnet_v4_councillor.name
        assert "sonnet" in claude_sonnet_v4_councillor.model_id.lower()

    def test_nova_pro_councillor(self):
        """Test Amazon Nova Pro councillor."""
        assert "Nova Pro" in nova_pro_councillor.name
        assert "nova-pro" in nova_pro_councillor.model_id.lower()

    def test_nova_lite_councillor(self):
        """Test Nova Lite councillor."""
        assert "Nova Lite" in nova_lite_councillor.name
        assert "nova" in nova_lite_councillor.model_id.lower()

    def test_llama_councillor(self):
        """Test Llama councillor."""
        assert "Llama" in llama_councillor.name
        assert "llama" in llama_councillor.model_id.lower()

    def test_all_councillors_unique_names(self):
        """Test that all councillors have unique names."""
        councillors = [
            nova_premier_councillor,
            claude_sonnet_v4_councillor,
            nova_lite_councillor,
            llama_councillor,
            nova_pro_councillor,
        ]
        names = [c.name for c in councillors]
        assert len(names) == len(set(names)), "Councillor names should be unique"

    def test_all_councillors_have_model_ids(self):
        """Test that all councillors have valid model IDs."""
        councillors = [
            nova_premier_councillor,
            claude_sonnet_v4_councillor,
            nova_lite_councillor,
            llama_councillor,
            nova_pro_councillor,
        ]
        for councillor in councillors:
            assert councillor.model_id
            assert isinstance(councillor.model_id, str)
            assert len(councillor.model_id) > 0


class TestCouncillorInvocation:
    """Tests for councillor invocation (requires AWS credentials)."""

    @pytest.mark.skip(reason="Requires AWS credentials and makes real API calls")
    def test_councillor_invoke_simple(self):
        """Test simple invocation (skipped by default)."""
        councillor = nova_lite_councillor
        response = councillor.invoke("Say 'test' and nothing else.")
        assert response
        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.skip(reason="Requires AWS credentials and makes real API calls")
    def test_councillor_invoke_with_prompt(self, simple_goal):
        """Test invocation with a structured prompt (skipped by default)."""
        councillor = nova_lite_councillor
        prompt = f"Briefly respond to this goal in one sentence:\n{simple_goal}"
        response = councillor.invoke(prompt)
        assert response
        assert isinstance(response, str)
        assert len(response) > 10
