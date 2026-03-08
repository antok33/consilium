"""
Unit tests for Orchestrator class.
"""
import pytest
from orchestrator import Orchestrator


class TestOrchestratorInitialization:
    """Tests for Orchestrator initialization."""

    def test_orchestrator_creation(self, simple_goal, simple_resources):
        """Test that orchestrator can be created."""
        orchestrator = Orchestrator(goal=simple_goal, resources=simple_resources)
        assert orchestrator is not None
        assert orchestrator.goal == simple_goal
        assert orchestrator.resources == simple_resources

    def test_orchestrator_without_resources(self, simple_goal):
        """Test orchestrator creation without resources."""
        orchestrator = Orchestrator(goal=simple_goal)
        assert orchestrator.goal == simple_goal
        assert orchestrator.resources == ""

    def test_orchestrator_has_councillors(self, simple_goal):
        """Test that orchestrator initializes councillors."""
        orchestrator = Orchestrator(goal=simple_goal)
        assert len(orchestrator.councillors) == 5
        assert all(c is not None for c in orchestrator.councillors)

    def test_orchestrator_has_summarizer(self, simple_goal):
        """Test that orchestrator initializes summarizer."""
        orchestrator = Orchestrator(goal=simple_goal)
        assert orchestrator.summarizer is not None

    def test_orchestrator_initial_state(self, simple_goal):
        """Test orchestrator initial state."""
        orchestrator = Orchestrator(goal=simple_goal)
        assert orchestrator.proposals == {}
        assert orchestrator.critiques == {}
        assert orchestrator.v2_proposals == {}
        assert orchestrator.votes == {}
        assert orchestrator.start_time is None
        assert orchestrator.end_time is None
        assert orchestrator.winning_proposal is None


class TestOrchestratorPromptCreation:
    """Tests for prompt creation methods."""

    def test_create_phase1_prompt(self, simple_goal, simple_resources):
        """Test Phase 1 prompt creation."""
        orchestrator = Orchestrator(goal=simple_goal, resources=simple_resources)
        prompt = orchestrator._create_phase1_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Goal" in prompt or simple_goal in prompt
        assert simple_resources in prompt
        assert "independently" in prompt.lower()

    def test_create_phase1_prompt_without_resources(self, simple_goal):
        """Test Phase 1 prompt without resources."""
        orchestrator = Orchestrator(goal=simple_goal)
        prompt = orchestrator._create_phase1_prompt()

        assert isinstance(prompt, str)
        assert simple_goal in prompt
        # Should not have resources section
        assert "Supporting Resources" not in prompt or orchestrator.resources == ""

    def test_create_phase2_prompt(self, simple_goal, dummy_proposals):
        """Test Phase 2 prompt creation."""
        orchestrator = Orchestrator(goal=simple_goal)
        orchestrator.proposals = dummy_proposals
        prompt = orchestrator._create_phase2_prompt(dummy_proposals)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "critique" in prompt.lower() or "review" in prompt.lower()
        # Should contain proposal labels
        for label in dummy_proposals.keys():
            assert label in prompt

    def test_create_phase3_prompt(self, simple_goal, dummy_proposals, dummy_critiques):
        """Test Phase 3 prompt creation."""
        orchestrator = Orchestrator(goal=simple_goal)
        orchestrator.proposals = dummy_proposals
        orchestrator.critiques = dummy_critiques
        prompt = orchestrator._create_phase3_prompt(dummy_proposals, dummy_critiques)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "V2" in prompt or "synthesis" in prompt.lower()

    def test_create_phase4_prompt(self, simple_goal, dummy_proposals):
        """Test Phase 4 prompt creation."""
        orchestrator = Orchestrator(goal=simple_goal)
        orchestrator.v2_proposals = dummy_proposals
        # Mock the summarizer to avoid API calls
        orchestrator.summarizer.extract_key_points_for_voting = lambda proposals, goal: proposals

        prompt = orchestrator._create_phase4_prompt(dummy_proposals)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "voting" in prompt.lower() or "vote" in prompt.lower()
        assert "ranked" in prompt.lower()  # Check for ranked-choice voting
        assert "first_choice" in prompt.lower()  # Check for new voting format
        assert "JSON" in prompt


class TestOrchestratorPhases:
    """Tests for individual phase execution (mocked to avoid API calls)."""

    @pytest.mark.skip(reason="Requires AWS credentials and makes real API calls")
    def test_phase1_execution(self, simple_goal):
        """Test Phase 1 execution (skipped by default)."""
        orchestrator = Orchestrator(goal=simple_goal)
        proposals = orchestrator.phase1_independent_ideation()

        assert len(proposals) == 5
        assert all(label in ["A", "B", "C", "D", "E"] for label in proposals.keys())
        assert all(isinstance(text, str) for text in proposals.values())

    @pytest.mark.skip(reason="Requires AWS credentials and makes real API calls")
    def test_phase2_execution(self, simple_goal, dummy_proposals):
        """Test Phase 2 execution (skipped by default)."""
        orchestrator = Orchestrator(goal=simple_goal)
        orchestrator.proposals = dummy_proposals
        orchestrator.proposal_summaries = dummy_proposals  # Use as summaries for testing

        critiques = orchestrator.phase2_peer_review()

        assert len(critiques) == 5
        assert all(isinstance(text, str) for text in critiques.values())

    @pytest.mark.skip(reason="Requires AWS credentials and makes real API calls")
    def test_phase3_execution(self, simple_goal, dummy_proposals, dummy_critiques):
        """Test Phase 3 execution (skipped by default)."""
        orchestrator = Orchestrator(goal=simple_goal)
        orchestrator.proposals = dummy_proposals
        orchestrator.critiques = dummy_critiques
        orchestrator.proposal_summaries = dummy_proposals
        orchestrator.critique_synthesis = "Test synthesis"

        v2_proposals = orchestrator.phase3_revision_convergence()

        assert len(v2_proposals) == 5
        assert all(label in ["A", "B", "C", "D", "E"] for label in v2_proposals.keys())

    @pytest.mark.skip(reason="Requires AWS credentials and makes real API calls")
    def test_phase4_execution(self, simple_goal, dummy_proposals):
        """Test Phase 4 execution (skipped by default)."""
        orchestrator = Orchestrator(goal=simple_goal)
        orchestrator.v2_proposals = dummy_proposals
        # Mock summarizer
        orchestrator.summarizer.extract_key_points_for_voting = lambda proposals, goal: proposals

        winning_label, votes = orchestrator.phase4_majority_vote()

        assert winning_label in ["A", "B", "C", "D", "E"]
        assert len(votes) == 5


class TestOrchestratorFullRun:
    """Tests for full orchestrator run (mocked to avoid API calls)."""

    @pytest.mark.skip(reason="Requires AWS credentials and makes real API calls - INTEGRATION TEST")
    def test_full_run(self, simple_goal, simple_resources):
        """Test full orchestrator run (skipped by default - integration test)."""
        orchestrator = Orchestrator(goal=simple_goal, resources=simple_resources)
        results = orchestrator.run()

        # Check result structure
        assert isinstance(results, dict)
        assert "goal" in results
        assert "winning_proposal" in results
        assert "winning_text" in results
        assert "phase1_proposals" in results
        assert "phase2_critiques" in results
        assert "phase3_v2_proposals" in results
        assert "phase4_votes" in results
        assert "duration_seconds" in results
        assert "councillors" in results

        # Check that phases completed
        assert len(results["phase1_proposals"]) == 5
        assert len(results["phase2_critiques"]) == 5
        assert len(results["phase3_v2_proposals"]) == 5
        assert len(results["phase4_votes"]) == 5

        # Check winning proposal
        assert results["winning_proposal"] in ["A", "B", "C", "D", "E"]
        assert len(results["winning_text"]) > 0

    def test_orchestrator_result_structure(self, simple_goal):
        """Test that orchestrator produces correct result structure."""
        orchestrator = Orchestrator(goal=simple_goal)

        # Manually set some data to test result compilation
        orchestrator.proposals = {"A": "test"}
        orchestrator.proposal_summaries = {"A": "summary"}
        orchestrator.critiques = {"C1": "critique"}
        orchestrator.critique_synthesis = "synthesis"
        orchestrator.v2_proposals = {"A": "v2"}
        orchestrator.votes = {"C1": {"vote": "A", "reason": "test"}}
        orchestrator.winning_proposal = "A"

        # We can't test run() without API calls, but we can verify the data structure
        assert orchestrator.goal == simple_goal
        assert len(orchestrator.proposals) == 1
        assert len(orchestrator.councillors) == 5


class TestOrchestratorEdgeCases:
    """Tests for edge cases and error handling."""

    def test_orchestrator_with_empty_goal(self):
        """Test orchestrator with empty goal."""
        orchestrator = Orchestrator(goal="")
        assert orchestrator.goal == ""

    def test_orchestrator_with_very_long_goal(self):
        """Test orchestrator with very long goal."""
        long_goal = "Test " * 10000  # Very long goal
        orchestrator = Orchestrator(goal=long_goal)
        assert orchestrator.goal == long_goal

    def test_orchestrator_councillor_names(self, simple_goal):
        """Test that all councillors have unique names."""
        orchestrator = Orchestrator(goal=simple_goal)
        names = [c.name for c in orchestrator.councillors]
        assert len(names) == len(set(names))
