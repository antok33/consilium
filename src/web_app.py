"""
Gradio web interface for Consilium.
"""
import gradio as gr
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from core import run_debate, save_final_proposal
from orchestrator import Orchestrator
import threading
import time

# Load environment variables
load_dotenv()


def process_goal_file(file):
    """
    Process uploaded goal file (MD or TXT).

    Args:
        file: Uploaded file object from Gradio

    Returns:
        Content of the file as string
    """
    if file is None:
        return ""

    try:
        file_path = Path(file.name)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {e}"


def process_resource_file(file):
    """
    Process uploaded resource file (MD or TXT).

    Args:
        file: Uploaded file object from Gradio

    Returns:
        Content of the file as string
    """
    if file is None:
        return ""

    try:
        file_path = Path(file.name)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {e}"


def run_council_debate(goal_text, goal_file, resource_text, resource_file, progress=gr.Progress()):
    """
    Run the council debate with provided inputs and show real-time progress.

    Args:
        goal_text: Goal text from textbox
        goal_file: Uploaded goal file
        resource_text: Resource text from textbox
        resource_file: Uploaded resource file
        progress: Gradio Progress tracker

    Yields:
        Tuples of (progress_log, status_message, final_proposal_text, download_file_path)
    """
    try:
        # Priority: file content > textbox content
        goal = ""
        if goal_file is not None:
            goal = process_goal_file(goal_file)
        elif goal_text.strip():
            goal = goal_text
        else:
            yield (
                "ERROR: Please provide a goal (either type it or upload a file)",
                "ERROR: No goal provided",
                "",
                None
            )
            return

        # Resource is optional
        resources = ""
        if resource_file is not None:
            resources = process_resource_file(resource_file)
        elif resource_text.strip():
            resources = resource_text

        # Initialize progress log with thread-safe access
        progress_log = []
        log_lock = threading.Lock()
        thread_exception = [None]
        results_container = [None]
        last_log_size = [0]

        def progress_callback(message):
            """Callback to capture progress messages (thread-safe)."""
            with log_lock:
                progress_log.append(message)

        # Initial message
        with log_lock:
            progress_log.append("Initializing debate...")
            progress_log.append(f"Council: 5 AI models")
            progress_log.append(f"Goal length: {len(goal)} characters")
            progress_log.append("")

        yield (
            "\n".join(progress_log),
            "Initializing...",
            "",
            None
        )

        # Create orchestrator with progress callback
        orchestrator = Orchestrator(
            goal=goal,
            resources=resources,
            progress_callback=progress_callback
        )

        # Run orchestrator in background thread
        def run_orchestrator():
            try:
                result = orchestrator.run()
                results_container[0] = result
            except Exception as e:
                thread_exception[0] = e

        # Start the orchestrator thread
        orchestrator_thread = threading.Thread(target=run_orchestrator)
        orchestrator_thread.start()

        # Poll progress log and yield updates in real-time
        while orchestrator_thread.is_alive():
            time.sleep(0.5)  # Poll every 500ms

            with log_lock:
                current_size = len(progress_log)
                if current_size > last_log_size[0]:
                    # New messages available
                    last_log_size[0] = current_size
                    status_msg = progress_log[-1] if progress_log else "Running..."
                    yield (
                        "\n".join(progress_log),
                        status_msg,
                        "",
                        None
                    )

        # Wait for thread to complete
        orchestrator_thread.join()

        # Check for exceptions
        if thread_exception[0]:
            raise thread_exception[0]

        # Get results
        results = results_container[0]
        if not results:
            raise ValueError("Orchestrator did not return results")

        # Save final proposal
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"final_proposal_{timestamp}.md"

        save_final_proposal(results, output_file)

        # Prepare display
        winning_text = results['winning_text']
        winning_label = results['winning_proposal']
        duration = results['duration_seconds']

        status_msg = f"✅ Debate completed in {duration:.1f} seconds\n"
        status_msg += f"🏆 Winning Proposal: {winning_label}\n\n"
        status_msg += "📊 Ranked-Choice Vote Breakdown:\n"

        for councillor_name, vote_data in results['phase4_votes'].items():
            # Check if this is ranked-choice voting (new format) or old format
            if 'first_choice' in vote_data:
                first = vote_data.get('first_choice', 'N/A')
                second = vote_data.get('second_choice', 'N/A')
                third = vote_data.get('third_choice', 'N/A')
                reason = vote_data.get('reason', 'No reason provided')
                status_msg += f"  • {councillor_name}:\n"
                status_msg += f"    1st: {first} (3pts) | 2nd: {second} (2pts) | 3rd: {third} (1pt)\n"
                status_msg += f"    Reason: {reason}\n\n"
            else:
                # Fallback for old single-vote format
                vote_label = vote_data.get('vote', 'N/A')
                reason = vote_data.get('reason', 'No reason provided')
                status_msg += f"  • {councillor_name}: {vote_label}\n"
                status_msg += f"    Reason: {reason}\n\n"

        # Final yield with complete results
        yield (
            "\n".join(progress_log),
            status_msg,
            winning_text,
            str(output_file)
        )

    except ValueError as e:
        error_log = "\n".join(progress_log) if 'progress_log' in locals() and progress_log else ""
        yield (
            error_log + f"\n\nERROR: {e}",
            f"ERROR: {e}",
            "",
            None
        )
    except Exception as e:
        error_log = "\n".join(progress_log) if 'progress_log' in locals() and progress_log else ""
        yield (
            error_log + f"\n\nERROR: Unexpected error: {e}",
            f"ERROR: Unexpected error: {e}",
            "",
            None
        )


def create_app():
    """
    Create and configure the Gradio app.

    Returns:
        Gradio Blocks app
    """
    with gr.Blocks(title="Consilium - Multi-Agent Debate") as app:
        gr.Markdown("""
        # 🏛️ Consilium - Multi-Agent LLM Debate System

        A collaborative decision-making system using **5 different AI models** to debate and
        reach consensus on complex problems through a structured 4-phase process.

        ## How it works:
        1. **Phase 1 - Independent Ideation**: Each AI independently proposes a solution
        2. **Phase 2 - Peer Review**: All AIs critique each other's proposals
        3. **Phase 3 - Revision**: Each AI creates a refined V2 proposal
        4. **Phase 4 - Voting**: All AIs vote on the best final proposal
        """)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📝 Goal Input")
                gr.Markdown("Provide your goal/problem statement:")

                goal_text = gr.Textbox(
                    label="Goal (Type Here)",
                    placeholder="Describe the problem or decision you want the council to address...",
                    lines=10
                )

                goal_file = gr.File(
                    label="Or Upload Goal File (MD/TXT)",
                    file_types=[".md", ".txt"],
                    type="filepath"
                )

                gr.Markdown("### 📎 Additional Resources (Optional)")

                resource_text = gr.Textbox(
                    label="Resources (Type Here)",
                    placeholder="Add any supporting context, constraints, budget info, etc...",
                    lines=6
                )

                resource_file = gr.File(
                    label="Or Upload Resource File (MD/TXT)",
                    file_types=[".md", ".txt"],
                    type="filepath"
                )

                run_btn = gr.Button("🚀 Start Council Debate", variant="primary", size="lg")

            with gr.Column(scale=1):
                gr.Markdown("### 📊 Real-Time Progress")

                progress_output = gr.Textbox(
                    label="Live Progress Log",
                    lines=15,
                    interactive=False
                )

                gr.Markdown("### 📈 Results")

                status_output = gr.Textbox(
                    label="Status & Vote Breakdown",
                    lines=10,
                    interactive=False
                )

                proposal_output = gr.Textbox(
                    label="Winning Proposal",
                    lines=15,
                    interactive=False
                )

                download_file = gr.File(
                    label="📥 Download Final Proposal"
                )

        # Examples
        gr.Markdown("### 💡 Examples")
        gr.Examples(
            examples=[
                [
                    "# Goal: Choose a Database for E-commerce Platform\n\nDecide which database to use for a new e-commerce platform that needs to handle:\n- High transaction volume (10K/day)\n- Product catalog with complex attributes\n- User sessions and shopping carts\n- Real-time inventory tracking\n\nOptions: PostgreSQL, MongoDB, or DynamoDB",
                    None,
                    "Budget: $2000/month\nExpected traffic: 10,000 users/day\nTeam: 3 backend developers\nTimeline: 3 months to launch",
                    None
                ],
                [
                    "# Goal: Design Authentication System\n\nDesign an authentication and authorization system for a SaaS application with:\n- Multi-tenancy support\n- Role-based access control (RBAC)\n- SSO integration\n- API key management",
                    None,
                    "Must comply with SOC 2\nTarget: 1000 organizations\nTimeline: 3 months\nTeam: 2 backend, 1 security engineer",
                    None
                ],
                [
                    "# Goal: Select CI/CD Pipeline\n\nChoose a CI/CD pipeline solution for our microservices architecture:\n- GitHub Actions\n- GitLab CI\n- Jenkins\n- CircleCI",
                    None,
                    "Team: 5 developers\nCurrent: GitHub for version control\nBudget: $500/month\nNeeds: Docker support, multi-environment deployment",
                    None
                ]
            ],
            inputs=[goal_text, goal_file, resource_text, resource_file]
        )

        # Connect the button - use generator for streaming updates
        run_btn.click(
            fn=run_council_debate,
            inputs=[goal_text, goal_file, resource_text, resource_file],
            outputs=[progress_output, status_output, proposal_output, download_file]
        )

        gr.Markdown("""
        ---
        **Note**: The debate process involves 5 AI models and 4 phases.
        Watch the progress log for real-time updates as each AI works through the process.

        **Models**: Amazon Nova Premier, Claude Sonnet 4, Amazon Nova Lite v2, Llama 3.3 70B, Amazon Nova Pro
        """)

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch()
