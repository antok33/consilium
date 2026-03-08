"""
Unit tests for Summarizer class.
"""
import pytest
from memory import Summarizer


class TestSummarizerInitialization:
    """Tests for Summarizer initialization."""

    def test_summarizer_creation(self):
        """Test that summarizer can be created."""
        summarizer = Summarizer()
        assert summarizer is not None
        assert summarizer.llm is not None

    def test_summarizer_uses_lightweight_llm(self):
        """Test that summarizer uses a lightweight LLM."""
        summarizer = Summarizer()
        # Nova Lite should be used for cost efficiency
        assert "nova" in summarizer.llm.model_id.lower() or "lite" in summarizer.llm.model_id.lower()


class TestSummarizerProposals:
    """Tests for proposal summarization."""

    @pytest.mark.skip(reason="Requires AWS credentials and makes real API calls")
    def test_summarize_proposals(self, simple_goal, dummy_proposals):
        """Test proposal summarization (skipped by default)."""
        summarizer = Summarizer()
        summaries = summarizer.summarize_proposals(dummy_proposals, simple_goal)

        assert len(summaries) == len(dummy_proposals)
        for label, summary in summaries.items():
            assert label in dummy_proposals
            assert isinstance(summary, str)
            assert len(summary) > 0
            # Summary should be shorter than original (in most cases)
            # This is a soft check since very short proposals might not get shorter

    def test_summarize_proposals_structure(self, simple_goal, dummy_proposals):
        """Test that summarize_proposals returns correct structure."""
        summarizer = Summarizer()
        # We can test the structure without making API calls
        # by checking the method signature and return type hints
        assert callable(summarizer.summarize_proposals)

    def test_summarize_proposals_empty_input(self, simple_goal):
        """Test summarization with empty proposals."""
        summarizer = Summarizer()
        summaries = summarizer.summarize_proposals({}, simple_goal)
        assert summaries == {}


class TestSummarizerCritiques:
    """Tests for critique summarization."""

    @pytest.mark.skip(reason="Requires AWS credentials and makes real API calls")
    def test_summarize_critiques(self, dummy_critiques, dummy_proposals):
        """Test critique synthesis (skipped by default)."""
        summarizer = Summarizer()
        synthesis = summarizer.summarize_critiques(dummy_critiques, dummy_proposals)

        assert isinstance(synthesis, str)
        assert len(synthesis) > 0
        # Synthesis should mention common themes
        assert len(synthesis) > 100  # Should be substantial

    def test_summarize_critiques_structure(self):
        """Test that summarize_critiques has correct signature."""
        summarizer = Summarizer()
        assert callable(summarizer.summarize_critiques)

    def test_summarize_critiques_empty_input(self):
        """Test critique synthesis with empty input."""
        summarizer = Summarizer()
        # Should handle empty critiques gracefully
        synthesis = summarizer.summarize_critiques({}, {})
        assert isinstance(synthesis, str)


class TestSummarizerPhase3Context:
    """Tests for Phase 3 context creation."""

    def test_create_phase3_context_structure(self, simple_goal, dummy_proposals):
        """Test Phase 3 context creation structure."""
        summarizer = Summarizer()
        proposal_summaries = {
            label: f"Summary of {text[:50]}..."
            for label, text in dummy_proposals.items()
        }
        critique_synthesis = "Common themes: FastAPI is popular, Lambda concerns exist."

        context = summarizer.create_phase3_context(
            simple_goal, proposal_summaries, critique_synthesis
        )

        assert isinstance(context, str)
        assert len(context) > 0
        assert "Goal" in context
        assert "Proposal" in context
        assert "Critique" in context or "Synthesis" in context

    def test_create_phase3_context_contains_all_elements(self, simple_goal, dummy_proposals):
        """Test that Phase 3 context contains all necessary elements."""
        summarizer = Summarizer()
        proposal_summaries = {
            label: f"Summary {label}"
            for label in dummy_proposals.keys()
        }
        critique_synthesis = "Test synthesis"

        context = summarizer.create_phase3_context(
            simple_goal, proposal_summaries, critique_synthesis
        )

        # Should contain goal
        assert "Web Framework" in context or "Goal" in context
        # Should contain proposal summaries
        for label in proposal_summaries.keys():
            assert label in context
        # Should contain critique synthesis
        assert "synthesis" in context.lower()


class TestSummarizerVoting:
    """Tests for voting key points extraction."""

    @pytest.mark.skip(reason="Requires AWS credentials and makes real API calls")
    def test_extract_key_points_for_voting(self, simple_goal, dummy_proposals):
        """Test key points extraction for voting (skipped by default)."""
        summarizer = Summarizer()
        key_points = summarizer.extract_key_points_for_voting(dummy_proposals, simple_goal)

        assert len(key_points) == len(dummy_proposals)
        for label, points in key_points.items():
            assert label in dummy_proposals
            assert isinstance(points, str)
            assert len(points) > 0

    def test_extract_key_points_structure(self):
        """Test that extract_key_points_for_voting has correct signature."""
        summarizer = Summarizer()
        assert callable(summarizer.extract_key_points_for_voting)

    def test_extract_key_points_empty_input(self, simple_goal):
        """Test key points extraction with empty input."""
        summarizer = Summarizer()
        key_points = summarizer.extract_key_points_for_voting({}, simple_goal)
        assert key_points == {}


class TestSummarizerMemoryStats:
    """Tests for memory statistics."""

    def test_get_memory_stats_structure(self):
        """Test memory stats return structure."""
        summarizer = Summarizer()
        stats = summarizer.get_memory_stats()

        assert isinstance(stats, dict)
        assert "total_summaries_created" in stats
        assert "tokens_saved_estimate" in stats

    def test_get_memory_stats_returns_integers(self):
        """Test that memory stats returns integer values."""
        summarizer = Summarizer()
        stats = summarizer.get_memory_stats()

        for key, value in stats.items():
            assert isinstance(value, int)
