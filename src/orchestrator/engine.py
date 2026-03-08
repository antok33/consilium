"""
Orchestrator Engine for Multi-Agent Debate and Iterative Refinement Protocol.
"""
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime
from councillors import (
    Councillor,
    nova_premier_councillor,
    claude_sonnet_v4_councillor,
    nova_lite_councillor,
    llama_councillor,
    nova_pro_councillor,
)
from memory import Summarizer


class Orchestrator:
    """
    Orchestrates the 4-phase multi-agent debate process.

    Phases:
    1. Independent Ideation (Divergence)
    2. Peer Review & Critique (Cross-Examination)
    3. Revision & Convergence
    4. Majority Vote (Consensus)
    """

    def __init__(self, goal: str, resources: str = "", progress_callback=None):
        """
        Initialize the orchestrator.

        Args:
            goal: The main goal/problem statement
            resources: Additional resources and context
            progress_callback: Optional callback function for progress updates
                               Signature: callback(message: str)
        """
        self.goal = goal
        self.resources = resources
        self.progress_callback = progress_callback
        self.councillors: List[Councillor] = [
            nova_premier_councillor,
            claude_sonnet_v4_councillor,
            nova_lite_councillor,
            llama_councillor,
            nova_pro_councillor,
        ]

        # Storage for each phase
        self.proposals: Dict[str, str] = {}  # Phase 1: Proposal label -> proposal text
        self.critiques: Dict[str, str] = {}  # Phase 2: Councillor name -> critique
        self.v2_proposals: Dict[str, str] = {}  # Phase 3: Proposal label -> V2 text
        self.votes: Dict[str, Dict[str, str]] = {}  # Phase 4: Councillor name -> vote data
        self.councillor_to_label: Dict[str, str] = {}  # Maps councillor name -> proposal label (for self-vote prevention)

        # Memory and summarization
        self.summarizer = Summarizer()
        self.proposal_summaries: Dict[str, str] = {}  # Summarized proposals
        self.critique_synthesis: str = ""  # Synthesized critiques
        self.summarization_threshold = 50000  # Only summarize if content > 50K chars

        # Metadata
        self.start_time = None
        self.end_time = None
        self.winning_proposal = None

    def _log_progress(self, message: str):
        """
        Log progress message to console and callback if provided.

        Args:
            message: Progress message to log
        """
        print(message)
        if self.progress_callback:
            self.progress_callback(message)

    def _create_phase1_prompt(self) -> str:
        """Create the prompt for Phase 1: Independent Ideation."""
        prompt = f"""You are participating in a multi-agent council debate to solve an important problem.

# Your Task

You will independently propose a solution to the goal described below. Your proposal should be detailed, well-reasoned, and actionable.

# Goal

{self.goal}
"""
        if self.resources.strip():
            prompt += f"""
# Supporting Resources

{self.resources}
"""

        prompt += """
# Instructions

Provide your proposal in the following format:

## Proposal: [Brief Title]

### Summary
[2-3 sentence overview of your approach]

### Detailed Plan
[Step-by-step explanation of your solution, covering all aspects of the goal]

### Key Advantages
- [Advantage 1]
- [Advantage 2]
- [Advantage 3]

### Technology Choices
[Specific frameworks, tools, and technologies you recommend]

### Trade-offs and Considerations
[What trade-offs does your approach make? What are the risks?]

### Implementation Approach
[How would you phase the implementation?]

Remember: You are proposing independently. Other councillors are doing the same without seeing your proposal.
"""
        return prompt

    def phase1_independent_ideation(self) -> Dict[str, str]:
        """
        Phase 1: Independent Ideation (Divergence)

        Each councillor independently proposes a solution without seeing others' proposals.

        Returns:
            Dictionary mapping proposal labels (A, B, C, D, E) to proposal text
        """
        self._log_progress("\n" + "=" * 80)
        self._log_progress("PHASE 1: INDEPENDENT IDEATION (DIVERGENCE)")
        self._log_progress("=" * 80)
        self._log_progress("Each councillor independently proposes a solution...")
        self._log_progress("")

        prompt = self._create_phase1_prompt()
        labels = ["A", "B", "C", "D", "E"]
        proposals = {}

        for i, councillor in enumerate(self.councillors):
            label = labels[i]
            self._log_progress(f"[{label}] Requesting proposal from {councillor.name}...")

            try:
                response = councillor.invoke(prompt)
                proposals[label] = response
                # Track which councillor created which proposal (for self-voting prevention)
                self.councillor_to_label[councillor.name] = label
                self._log_progress(f"[{label}] ✓ Proposal received ({len(response)} chars)")
            except Exception as e:
                self._log_progress(f"[{label}] ✗ ERROR: {e}")
                proposals[label] = f"Error generating proposal: {e}"
                self.councillor_to_label[councillor.name] = label

        self.proposals = proposals
        self._log_progress(f"\n✓ Phase 1 complete. {len(proposals)} proposals collected.")

        # Conditional summarization: Only summarize if total content exceeds threshold
        total_chars = sum(len(text) for text in proposals.values())
        self._log_progress(f"\n[Memory] Total content: {total_chars:,} characters")

        if total_chars > self.summarization_threshold:
            self._log_progress(f"[Memory] Content exceeds {self.summarization_threshold:,} chars. Summarizing proposals...")
            self.proposal_summaries = self.summarizer.summarize_proposals(proposals, self.goal)
            summary_chars = sum(len(text) for text in self.proposal_summaries.values())
            reduction = ((total_chars - summary_chars) / total_chars * 100) if total_chars > 0 else 0
            self._log_progress(f"[Memory] Summarization complete: {total_chars:,} → {summary_chars:,} chars ({reduction:.1f}% reduction)")
        else:
            self._log_progress(f"[Memory] Content under threshold. Skipping summarization.")

        return proposals

    def _create_phase2_prompt(self, proposals: Dict[str, str]) -> str:
        """Create the prompt for Phase 2: Peer Review & Critique."""
        # Use summaries if available, otherwise use full proposals
        proposals_to_use = self.proposal_summaries if self.proposal_summaries else proposals

        proposals_text = "\n\n".join([
            f"## Proposal {label}\n\n{text}"
            for label, text in proposals_to_use.items()
        ])

        prompt = f"""You are reviewing proposals from a multi-agent council debate.

# Goal Being Addressed

{self.goal}

# All Proposals

{proposals_text}

# Your Task

Review each proposal critically and constructively. For each proposal:

1. **Identify strengths** - What does this proposal do well?
2. **Identify weaknesses or risks** - What are the potential problems?
3. **Highlight ideas worth adopting** - What specific ideas should be incorporated?

Then provide an overall summary of which patterns and ideas appear most promising across all proposals.

# Required Format

## Critique

### Proposal A
**Strengths:**
[List strengths]

**Weaknesses:**
[List weaknesses]

**Ideas Worth Adopting:**
[List specific ideas]

### Proposal B
[Same structure]

### Proposal C
[Same structure]

### Proposal D
[Same structure]

### Proposal E
[Same structure]

### Overall Insights
[2-3 paragraphs summarizing the best patterns and ideas emerging across all proposals]
"""
        return prompt

    def phase2_peer_review(self) -> Dict[str, str]:
        """
        Phase 2: Peer Review & Critique (Cross-Examination)

        Each councillor reviews all proposals and provides structured critique.

        Returns:
            Dictionary mapping councillor names to their critiques
        """
        self._log_progress("\n" + "=" * 80)
        self._log_progress("PHASE 2: PEER REVIEW & CRITIQUE (CROSS-EXAMINATION)")
        self._log_progress("=" * 80)
        self._log_progress("Each councillor reviews all proposals...")
        self._log_progress("")

        prompt = self._create_phase2_prompt(self.proposals)
        critiques = {}

        for councillor in self.councillors:
            self._log_progress(f"Requesting critique from {councillor.name}...")

            try:
                response = councillor.invoke(prompt)
                critiques[councillor.name] = response
                self._log_progress(f"✓ Critique received from {councillor.name} ({len(response)} chars)")
            except Exception as e:
                self._log_progress(f"✗ ERROR from {councillor.name}: {e}")
                critiques[councillor.name] = f"Error generating critique: {e}"

        self.critiques = critiques
        self._log_progress(f"\n✓ Phase 2 complete. {len(critiques)} critiques collected.")

        # Conditional summarization: Only synthesize if total content exceeds threshold
        total_chars = sum(len(text) for text in critiques.values())
        self._log_progress(f"\n[Memory] Total critique content: {total_chars:,} characters")

        if total_chars > self.summarization_threshold:
            self._log_progress(f"[Memory] Content exceeds {self.summarization_threshold:,} chars. Synthesizing critiques...")
            self.critique_synthesis = self.summarizer.summarize_critiques(critiques, self.proposals)
            synthesis_chars = len(self.critique_synthesis)
            reduction = ((total_chars - synthesis_chars) / total_chars * 100) if total_chars > 0 else 0
            self._log_progress(f"[Memory] Synthesis complete: {total_chars:,} → {synthesis_chars:,} chars ({reduction:.1f}% reduction)")
        else:
            self._log_progress(f"[Memory] Content under threshold. Skipping synthesis.")

        return critiques

    def _create_phase3_prompt(self, proposals: Dict[str, str], critiques: Dict[str, str]) -> str:
        """Create the prompt for Phase 3: Revision & Convergence."""
        # Use compressed context for efficiency
        context = self.summarizer.create_phase3_context(
            self.goal,
            self.proposal_summaries if self.proposal_summaries else proposals,
            self.critique_synthesis if self.critique_synthesis else "\n\n".join([
                f"## Critique from {name}\n\n{text}"
                for name, text in critiques.items()
            ])
        )

        prompt = f"""You are synthesizing the best ideas from a multi-agent council debate.

{context}

# Your Task

Based on all the proposals and critiques, write a **Version 2 (V2)** solution that:

1. Incorporates the strongest ideas from across all proposals
2. Addresses the weaknesses identified in the critiques
3. Creates a cohesive, comprehensive solution

Your V2 should be a refined hybrid that represents the collective wisdom of the council.

# Required Format

## V2 Proposal: [Title]

### Executive Summary
[2-3 sentences capturing the essence of the solution]

### Architecture & Design
[Detailed technical architecture incorporating the best ideas]

### Technology Stack
[Specific choices with rationale]

### Implementation Plan
[Phased approach to building the system]

### Risk Mitigation
[How you address the concerns raised in critiques]

### Why This Synthesis Works
[Brief explanation of how you combined the best ideas]
"""
        return prompt

    def phase3_revision_convergence(self) -> Dict[str, str]:
        """
        Phase 3: Revision & Convergence

        Each councillor creates a V2 proposal incorporating the best ideas.

        Returns:
            Dictionary mapping proposal labels to V2 proposal text
        """
        self._log_progress("\n" + "=" * 80)
        self._log_progress("PHASE 3: REVISION & CONVERGENCE")
        self._log_progress("=" * 80)
        self._log_progress("Each councillor creates a refined V2 proposal...")
        self._log_progress("")

        prompt = self._create_phase3_prompt(self.proposals, self.critiques)
        labels = ["A", "B", "C", "D", "E"]
        v2_proposals = {}

        for i, councillor in enumerate(self.councillors):
            label = labels[i]
            self._log_progress(f"[{label}] Requesting V2 proposal from {councillor.name}...")

            try:
                response = councillor.invoke(prompt)
                v2_proposals[label] = response
                self._log_progress(f"[{label}] ✓ V2 proposal received ({len(response)} chars)")
            except Exception as e:
                self._log_progress(f"[{label}] ✗ ERROR: {e}")
                v2_proposals[label] = f"Error generating V2 proposal: {e}"

        self.v2_proposals = v2_proposals
        self._log_progress(f"\n✓ Phase 3 complete. {len(v2_proposals)} V2 proposals collected.")

        # Extract key points for voting
        self._log_progress("\n[Memory] Extracting key points for voting...")

        return v2_proposals

    def _create_phase4_prompt(self, v2_proposals: Dict[str, str], exclude_label: str = None) -> str:
        """
        Create the prompt for Phase 4: Ranked-Choice Vote.

        Args:
            v2_proposals: Dictionary of V2 proposals
            exclude_label: Optional label to exclude (for self-voting prevention)
        """
        # Extract key points for efficient voting
        v2_key_points = self.summarizer.extract_key_points_for_voting(v2_proposals, self.goal)

        # Exclude the councillor's own proposal if specified
        proposals_to_vote = {
            label: text for label, text in v2_key_points.items()
            if label != exclude_label
        }

        proposals_text = "\n\n".join([
            f"## V2 Proposal {label}\n\n{text}"
            for label, text in proposals_to_vote.items()
        ])

        exclude_note = ""
        if exclude_label:
            exclude_note = f"\n\nNote: You cannot vote for Proposal {exclude_label} as it is your own proposal."

        prompt = f"""You are voting on the final solution in a multi-agent council debate using ranked-choice voting.

# Goal Being Addressed

{self.goal}

# V2 Proposals Available for Voting

{proposals_text}{exclude_note}

# Your Task

Review all V2 proposals and provide your RANKED PREFERENCES (1st, 2nd, 3rd choice):
- **1st choice** (3 points): The proposal that best solves the goal
- **2nd choice** (2 points): Your second preference
- **3rd choice** (1 point): Your third preference

Rank the proposals based on:
1. How well they solve the goal
2. Practicality and implementability
3. Integration of council's shared insights

# Required Format

Respond with ONLY valid JSON in this exact format:

{{
  "first_choice": "A",
  "second_choice": "B",
  "third_choice": "C",
  "reason": "Brief explanation of your ranking rationale."
}}

Replace X with A, B, C, D, or E. Do not include any text before or after the JSON.
"""
        return prompt

    def phase4_majority_vote(self) -> Tuple[str, Dict[str, Dict[str, Any]]]:
        """
        Phase 4: Ranked-Choice Vote (Consensus)

        Each councillor ranks proposals (1st, 2nd, 3rd choice) using ranked-choice voting.
        Points: 1st choice = 3 points, 2nd choice = 2 points, 3rd choice = 1 point
        Self-voting is prevented: councillors cannot rank their own proposals.

        Returns:
            Tuple of (winning_proposal_label, votes_dict)
        """
        self._log_progress("\n" + "=" * 80)
        self._log_progress("PHASE 4: RANKED-CHOICE VOTE (CONSENSUS)")
        self._log_progress("=" * 80)
        self._log_progress("Each councillor ranks proposals (1st, 2nd, 3rd choice)...")
        self._log_progress("Self-voting is disabled: councillors cannot vote for their own proposals.")
        self._log_progress("")

        votes = {}
        point_tally = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}

        for councillor in self.councillors:
            # Get this councillor's proposal label for self-vote prevention
            exclude_label = self.councillor_to_label.get(councillor.name, None)

            self._log_progress(f"Requesting ranked vote from {councillor.name}...")
            if exclude_label:
                self._log_progress(f"  (Excluding their own proposal: {exclude_label})")

            try:
                # Create personalized prompt that excludes their own proposal
                prompt = self._create_phase4_prompt(self.v2_proposals, exclude_label=exclude_label)
                response = councillor.invoke(prompt)

                # Try to parse JSON from the response
                response_clean = response.strip()
                if not response_clean.startswith("{"):
                    # Try to find JSON in the response
                    start = response_clean.find("{")
                    end = response_clean.rfind("}") + 1
                    if start != -1 and end > start:
                        response_clean = response_clean[start:end]

                vote_data = json.loads(response_clean)

                # Extract ranked choices
                first = vote_data.get("first_choice", "").strip().upper()
                second = vote_data.get("second_choice", "").strip().upper()
                third = vote_data.get("third_choice", "").strip().upper()
                reason = vote_data.get("reason", "No reason provided")

                # Validate votes
                valid_votes = []
                if first in point_tally and first != exclude_label:
                    valid_votes.append(("1st", first, 3))
                if second in point_tally and second != exclude_label and second != first:
                    valid_votes.append(("2nd", second, 2))
                if third in point_tally and third != exclude_label and third not in [first, second]:
                    valid_votes.append(("3rd", third, 1))

                # Award points
                for rank, label, points in valid_votes:
                    point_tally[label] += points

                votes[councillor.name] = {
                    "first_choice": first,
                    "second_choice": second,
                    "third_choice": third,
                    "reason": reason,
                    "valid_votes": len(valid_votes)
                }

                self._log_progress(f"✓ {councillor.name}: 1st={first} (3pts), 2nd={second} (2pts), 3rd={third} (1pt)")

            except json.JSONDecodeError as e:
                self._log_progress(f"✗ ERROR: {councillor.name} - JSON parse error: {e}")
                self._log_progress(f"  Response: {response[:200]}...")
                votes[councillor.name] = {
                    "first_choice": "ERROR",
                    "second_choice": "ERROR",
                    "third_choice": "ERROR",
                    "reason": f"JSON parse error: {e}",
                    "valid_votes": 0
                }
            except Exception as e:
                self._log_progress(f"✗ ERROR from {councillor.name}: {e}")
                votes[councillor.name] = {
                    "first_choice": "ERROR",
                    "second_choice": "ERROR",
                    "third_choice": "ERROR",
                    "reason": str(e),
                    "valid_votes": 0
                }

        self.votes = votes

        # Determine winner by points
        self._log_progress("\n" + "-" * 80)
        self._log_progress("RANKED-CHOICE VOTE TALLY (Points: 1st=3, 2nd=2, 3rd=1):")
        sorted_results = sorted(point_tally.items(), key=lambda x: x[1], reverse=True)
        for label, points in sorted_results:
            self._log_progress(f"  Proposal {label}: {points} point(s)")

        # Find winner (handle ties)
        max_points = max(point_tally.values())
        winners = [label for label, points in point_tally.items() if points == max_points]

        if len(winners) > 1:
            self._log_progress(f"\n⚠ TIE detected: {', '.join(winners)} all have {max_points} points")
            self._log_progress(f"  Breaking tie by choosing first alphabetically: {winners[0]}")
            winning_label = winners[0]
        else:
            winning_label = winners[0]

        self._log_progress("-" * 80)
        self._log_progress(f"🏆 WINNER: Proposal {winning_label} with {max_points} points")

        self.winning_proposal = winning_label
        self._log_progress(f"\n✓ Phase 4 complete.")

        return winning_label, votes

    def run(self) -> Dict[str, Any]:
        """
        Execute the complete 4-phase debate process.

        Returns:
            Dictionary containing all results
        """
        self.start_time = datetime.now()

        self._log_progress("\n🚀 Starting Multi-Agent Debate Process...")
        self._log_progress(f"Council size: {len(self.councillors)} councillors")
        self._log_progress(f"Models: {', '.join([c.name for c in self.councillors])}")

        # Execute all 4 phases
        self.phase1_independent_ideation()
        self.phase2_peer_review()
        self.phase3_revision_convergence()
        winning_label, votes = self.phase4_majority_vote()

        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        # Compile results
        results = {
            "goal": self.goal,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": duration,
            "councillors": [c.name for c in self.councillors],
            "winning_proposal": winning_label,
            "winning_text": self.v2_proposals.get(winning_label, ""),
            "phase1_proposals": self.proposals,
            "phase1_summaries": self.proposal_summaries,
            "phase2_critiques": self.critiques,
            "phase2_synthesis": self.critique_synthesis,
            "phase3_v2_proposals": self.v2_proposals,
            "phase4_votes": votes,
        }

        self._log_progress("\n" + "=" * 80)
        self._log_progress(f"✅ DEBATE COMPLETE (Duration: {duration:.1f} seconds)")
        self._log_progress("=" * 80)

        return results
