"""
Core debate logic - separated from CLI/UI concerns.
"""
from pathlib import Path
from orchestrator import Orchestrator


def run_debate(goal: str, resources: str = "", progress_callback=None) -> dict:
    """
    Run the multi-agent debate with the given goal and resources.

    Args:
        goal: The goal/problem statement for the council
        resources: Additional resources and context (optional)
        progress_callback: Optional callback for progress updates

    Returns:
        Dictionary containing all debate results
    """
    print("=" * 80)
    print("Multi-Agent Debate and Iterative Refinement Protocol")
    print("=" * 80)
    print()

    if not goal.strip():
        raise ValueError("Goal cannot be empty")

    print("Council Goal:")
    print("-" * 80)
    print(goal)
    print("-" * 80)
    print()

    if resources.strip():
        print("Additional Resources:")
        print("-" * 80)
        print(resources)
        print("-" * 80)
        print()

    # Initialize orchestrator and start the 4-phase process
    orchestrator = Orchestrator(goal=goal, resources=resources, progress_callback=progress_callback)
    results = orchestrator.run()

    # Display final results
    print("\n" + "=" * 80)
    print("FINAL WINNING PROPOSAL")
    print("=" * 80)
    print(f"\nWINNER: Proposal {results['winning_proposal']}")
    print("\n" + "-" * 80)
    print(results['winning_text'])
    print("-" * 80)

    print("\nRanked-Choice Vote Breakdown:")
    for councillor_name, vote_data in results['phase4_votes'].items():
        # Check if this is ranked-choice voting (new format)
        if 'first_choice' in vote_data:
            first = vote_data.get('first_choice', 'N/A')
            second = vote_data.get('second_choice', 'N/A')
            third = vote_data.get('third_choice', 'N/A')
            reason = vote_data.get('reason', 'No reason provided')
            print(f"\n  {councillor_name}:")
            print(f"    1st: {first} (3pts) | 2nd: {second} (2pts) | 3rd: {third} (1pt)")
            print(f"    Reason: {reason}")
        else:
            # Fallback for old single-vote format
            vote_label = vote_data.get('vote', 'N/A')
            reason = vote_data.get('reason', 'No reason provided')
            print(f"\n  {councillor_name}: Proposal {vote_label}")
            print(f"    Reason: {reason}")

    print("\n" + "=" * 80)
    print(f"Process completed in {results['duration_seconds']:.1f} seconds")
    print("=" * 80)

    return results


def save_final_proposal(results: dict, output_path: Path) -> None:
    """
    Save the final winning proposal to a file.

    Args:
        results: Results dictionary from the orchestrator
        output_path: Path to save the final proposal
    """
    winning_label = results['winning_proposal']
    winning_text = results['winning_text']
    duration = results['duration_seconds']
    councillors = results['councillors']
    votes = results['phase4_votes']

    # Create the final proposal document
    content = f"""# Final Council Decision - Proposal {winning_label}

**Date**: {results['end_time']}
**Duration**: {duration:.1f} seconds
**Councillors**: {', '.join(councillors)}

---

## Voting Results

"""

    # Add vote breakdown - handle both ranked-choice and old single-vote format
    point_tally = {}
    vote_count_tally = {}

    for councillor_name, vote_data in votes.items():
        # Check if this is ranked-choice voting
        if 'first_choice' in vote_data:
            # New ranked-choice format
            first = vote_data.get('first_choice', '')
            second = vote_data.get('second_choice', '')
            third = vote_data.get('third_choice', '')

            # Award points
            for label, points in [(first, 3), (second, 2), (third, 1)]:
                if label and label != 'ERROR' and label != 'INVALID':
                    point_tally[label] = point_tally.get(label, 0) + points
        else:
            # Old single-vote format (fallback)
            vote_label = vote_data.get('vote', '')
            if vote_label and vote_label != 'ERROR' and vote_label != 'INVALID':
                vote_count_tally[vote_label] = vote_count_tally.get(vote_label, 0) + 1

    # Display results based on voting format used
    if point_tally:
        content += "**Ranked-Choice Vote Tally (Points: 1st=3, 2nd=2, 3rd=1):**\n\n"
        for label in sorted(point_tally.keys(), key=lambda x: point_tally[x], reverse=True):
            points = point_tally[label]
            marker = "[WINNER]" if label == winning_label else "        "
            content += f"{marker} Proposal {label}: {points} point(s)\n"
    else:
        content += "**Vote Tally:**\n\n"
        for label in sorted(vote_count_tally.keys()):
            count = vote_count_tally[label]
            marker = "[WINNER]" if label == winning_label else "        "
            content += f"{marker} Proposal {label}: {count} vote(s)\n"

    content += "\n**Individual Votes:**\n\n"
    for councillor_name, vote_data in votes.items():
        if 'first_choice' in vote_data:
            # New ranked-choice format
            first = vote_data.get('first_choice', 'N/A')
            second = vote_data.get('second_choice', 'N/A')
            third = vote_data.get('third_choice', 'N/A')
            reason = vote_data.get('reason', 'No reason provided')
            content += f"- **{councillor_name}**:\n"
            content += f"  - 1st: {first} (3pts) | 2nd: {second} (2pts) | 3rd: {third} (1pt)\n"
            content += f"  - Reason: {reason}\n\n"
        else:
            # Old single-vote format
            vote_label = vote_data.get('vote', 'N/A')
            reason = vote_data.get('reason', 'No reason provided')
            content += f"- **{councillor_name}**: Proposal {vote_label}\n"
            content += f"  - Reason: {reason}\n\n"

    content += "---\n\n"
    content += "## Winning Proposal\n\n"
    content += winning_text

    # Write to file
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nFinal proposal saved to: {output_path}")
    except Exception as e:
        print(f"\nWARNING: Could not save final proposal: {e}")
