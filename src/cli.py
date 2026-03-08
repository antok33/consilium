"""
CLI interface for Consilium.
"""
import click
from pathlib import Path
from dotenv import load_dotenv
from core import run_debate, save_final_proposal

# Load environment variables
load_dotenv()


@click.group()
def cli():
    """
    Consilium - Multi-Agent LLM Debate System

    A system for collaborative decision-making using multiple LLMs.
    Inspired by Andrej Karpathy's llm-council.
    """
    pass


@cli.command()
@click.option(
    '--goal',
    '-g',
    help='Goal text directly as a string'
)
@click.option(
    '--goal-file',
    type=click.Path(exists=True, path_type=Path),
    help='Path to goal file (markdown or text)'
)
@click.option(
    '--resource',
    '-r',
    help='Resource text directly as a string'
)
@click.option(
    '--resource-file',
    type=click.Path(exists=True, path_type=Path),
    help='Path to resource file (markdown or text)'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(path_type=Path),
    default='output/final_proposal.md',
    help='Path to save final proposal'
)
def run(goal, goal_file, resource, resource_file, output):
    """
    Run the debate with provided goal and optional resources.

    You must provide either --goal or --goal-file.

    Examples:
        consilium run --goal-file my_goal.md
        consilium run --goal "Choose between FastAPI and Flask" --output results.md
        consilium run -g "My goal" -r "My context" -o output/proposal.md
    """
    try:
        # Get goal from file or direct input
        goal_text = ""
        if goal_file:
            with open(goal_file, 'r', encoding='utf-8') as f:
                goal_text = f.read()
        elif goal:
            goal_text = goal
        else:
            click.echo("ERROR: You must provide either --goal or --goal-file", err=True)
            click.echo("Example: consilium run --goal-file my_goal.md", err=True)
            raise click.Abort()

        if not goal_text.strip():
            click.echo("ERROR: Goal is empty", err=True)
            raise click.Abort()

        # Get resources from file or direct input (optional)
        resource_text = ""
        if resource_file:
            with open(resource_file, 'r', encoding='utf-8') as f:
                resource_text = f.read()
        elif resource:
            resource_text = resource

        # Run debate
        results = run_debate(goal_text, resource_text)

        # Save results
        save_final_proposal(results, output)

        click.echo(f"\nSuccess! Final proposal saved to: {output}")

    except FileNotFoundError as e:
        click.echo(f"ERROR: File not found: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"ERROR: {e}", err=True)
        raise click.Abort()


@cli.command('web-app')
@click.option(
    '--host',
    default='127.0.0.1',
    help='Host to bind the web server to'
)
@click.option(
    '--port',
    default=7860,
    type=int,
    help='Port to bind the web server to'
)
@click.option(
    '--share',
    is_flag=True,
    help='Create a public share link'
)
def web_app(host, port, share):
    """
    Launch the Gradio web interface.

    Starts a web server where users can input goals and resources
    through a browser interface. Supports file uploads for goals.

    Examples:
        consilium web-app
        consilium web-app --host 0.0.0.0 --port 8080
        consilium web-app --share
    """
    try:
        # Import here to avoid loading Gradio unless needed
        from web_app import create_app

        click.echo("Starting Consilium Web Interface...")
        click.echo(f"Host: {host}")
        click.echo(f"Port: {port}")

        app = create_app()
        app.launch(
            server_name=host,
            server_port=port,
            share=share
        )

    except ImportError as e:
        click.echo(f"ERROR: Failed to import web_app: {e}", err=True)
        click.echo("Make sure gradio is installed: uv pip install gradio", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"ERROR: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()
