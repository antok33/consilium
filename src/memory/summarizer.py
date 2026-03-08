"""
Memory Summarizer for Multi-Agent Debate Protocol.

This module handles summarization and compression of debate context
to manage token budgets and improve efficiency across phases.
"""
from typing import Dict, List
from councillors import nova_lite_councillor


class Summarizer:
    """
    Handles summarization and memory management for the debate process.

    Uses a lightweight LLM to compress proposals, critiques, and context
    while preserving key information for decision-making.
    """

    def __init__(self):
        """Initialize the summarizer with a lightweight LLM."""
        # Use Nova Lite for cost-effective summarization
        self.llm = nova_lite_councillor

    def summarize_proposals(self, proposals: Dict[str, str], goal: str) -> Dict[str, str]:
        """
        Summarize each proposal to extract key points.

        Args:
            proposals: Dictionary mapping labels (A, B, C, D, E) to full proposal text
            goal: The original goal being addressed

        Returns:
            Dictionary mapping labels to summarized proposals
        """
        print("\n[Memory] Summarizing proposals...")
        summaries = {}

        for label, proposal_text in proposals.items():
            prompt = f"""Summarize the following proposal concisely while preserving all key technical decisions and important details.

# Goal Being Addressed
{goal}

# Proposal {label}
{proposal_text}

# Instructions
Create a concise summary that captures:
1. The main architectural approach
2. Key technology choices and why
3. Important design decisions
4. Trade-offs mentioned
5. Implementation strategy

Keep the summary focused and under 500 words while preserving all critical information.

Summary:"""

            try:
                summary = self.llm.invoke(prompt)
                summaries[label] = summary
                print(f"  [Memory] Proposal {label} summarized ({len(proposal_text)} -> {len(summary)} chars)")
            except Exception as e:
                print(f"  [Memory] ERROR summarizing Proposal {label}: {e}")
                summaries[label] = proposal_text  # Fallback to original

        return summaries

    def summarize_critiques(self, critiques: Dict[str, str], proposals: Dict[str, str]) -> str:
        """
        Summarize all critiques into a unified set of insights.

        Args:
            critiques: Dictionary mapping councillor names to their critique text
            proposals: Dictionary of proposal labels to text (for context)

        Returns:
            A unified summary of all critiques highlighting key patterns
        """
        print("\n[Memory] Synthesizing critiques...")

        # Combine all critiques
        all_critiques = "\n\n".join([
            f"## Critique from {name}\n{text}"
            for name, text in critiques.items()
        ])

        prompt = f"""Analyze and synthesize the following critiques into a unified summary.

# All Critiques
{all_critiques}

# Instructions
Create a comprehensive synthesis that:

1. **Common Strengths Identified Across Proposals**
   - What patterns emerged as strong ideas?
   - Which approaches were praised by multiple reviewers?

2. **Common Weaknesses and Concerns**
   - What risks were identified repeatedly?
   - Which aspects need improvement?

3. **Key Ideas Worth Adopting**
   - What specific technical solutions should be incorporated?
   - Which design patterns received positive feedback?

4. **Critical Decision Points**
   - What are the main architectural choices to make?
   - Where do the proposals differ significantly?

Keep this synthesis focused and actionable, under 800 words.

Synthesis:"""

        try:
            synthesis = self.llm.invoke(prompt)
            print(f"  [Memory] Critiques synthesized ({len(all_critiques)} -> {len(synthesis)} chars)")
            return synthesis
        except Exception as e:
            print(f"  [Memory] ERROR synthesizing critiques: {e}")
            return all_critiques  # Fallback to all critiques

    def create_phase3_context(
        self,
        goal: str,
        proposal_summaries: Dict[str, str],
        critique_synthesis: str
    ) -> str:
        """
        Create optimized context for Phase 3 (Revision & Convergence).

        Args:
            goal: Original goal
            proposal_summaries: Summarized proposals
            critique_synthesis: Synthesized critiques

        Returns:
            Compressed context string for Phase 3
        """
        print("\n[Memory] Creating Phase 3 context...")

        proposals_text = "\n\n".join([
            f"### Proposal {label} (Summary)\n{summary}"
            for label, summary in proposal_summaries.items()
        ])

        context = f"""# Goal
{goal}

# Proposal Summaries (From Phase 1)
{proposals_text}

# Synthesized Critique Insights (From Phase 2)
{critique_synthesis}
"""

        print(f"  [Memory] Phase 3 context created ({len(context)} chars)")
        return context

    def extract_key_points_for_voting(self, v2_proposals: Dict[str, str], goal: str) -> Dict[str, str]:
        """
        Extract key decision points from V2 proposals for voting.

        Args:
            v2_proposals: Dictionary of V2 proposal labels to text
            goal: Original goal

        Returns:
            Dictionary mapping labels to extracted key points
        """
        print("\n[Memory] Extracting key points for voting...")
        key_points = {}

        for label, proposal_text in v2_proposals.items():
            prompt = f"""Extract the key decision points and differentiators from this proposal.

# Goal
{goal}

# V2 Proposal {label}
{proposal_text}

# Instructions
Extract:
1. Core architectural approach (in 2-3 sentences)
2. Main technology choices and rationale
3. Key differentiators from other approaches
4. Primary strengths
5. Main trade-offs accepted

Keep this under 300 words, focusing on what makes this proposal unique and strong.

Key Points:"""

            try:
                points = self.llm.invoke(prompt)
                key_points[label] = points
                print(f"  [Memory] Key points extracted for Proposal {label} ({len(proposal_text)} -> {len(points)} chars)")
            except Exception as e:
                print(f"  [Memory] ERROR extracting key points for Proposal {label}: {e}")
                key_points[label] = proposal_text  # Fallback to full text

        return key_points

    def get_memory_stats(self) -> Dict[str, int]:
        """
        Get statistics about memory/token usage.

        Returns:
            Dictionary with memory statistics
        """
        # Placeholder for future token tracking
        return {
            "total_summaries_created": 0,
            "tokens_saved_estimate": 0,
        }
