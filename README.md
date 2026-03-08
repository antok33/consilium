# Consilium - Multi-Agent LLM Debate System

> **Note**: This is a Sunday project exploring how multiple LLMs interact and collaborate when solving complex problems. The goal is to investigate whether diverse AI perspectives can lead to better decision-making through structured debate and consensus.
>
> **Inspiration**: This project is inspired by Andrej Karpathy's [llm-council](https://github.com/karpathy/llm-council) and builds upon the concept of multi-agent deliberation with additional features like real-time progress tracking, memory optimization, and a web interface.

---

A collaborative decision-making system using multiple LLMs to debate and reach consensus on complex problems through structured phases.

## Features

- **4-Phase Debate Process**: Independent ideation, peer review, revision, and ranked-choice voting
- **5 AI Models**: Leverages diverse AI perspectives (Amazon Nova Premier, Claude Sonnet 4, Amazon Nova Lite v2, Llama 3.3 70B, Amazon Nova Pro)
- **Ranked-Choice Voting**: Councillors rank proposals (1st, 2nd, 3rd) with point-based system (3-2-1)
- **Self-Voting Prevention**: Councillors cannot vote for their own proposals
- **Real-Time Progress**: Live updates showing which AI is working on what
- **Smart Memory Management**: Conditional summarization (only when content exceeds 50K characters)
- **Web Interface**: Gradio-based UI with file upload support
- **CLI Support**: Command-line interface for automation
- **Docker Ready**: Containerized deployment on port 8080

## Quick Start

### 1. Install

```bash
git clone <repo-url>
cd consilium
make install
```

### 2. Configure AWS

Create `.env` file (copy from `.env.example`):

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

### 3. Launch Web Interface

```bash
make web-app
```

Open http://localhost:7860 and start debating!

## Usage

### Web Interface (Recommended)

```bash
# Launch locally
make web-app

# Custom port
uv run python src/cli.py web-app --port 8080 --host 0.0.0.0

# Public share link
uv run python src/cli.py web-app --share
```

**Features:**
- Type or upload goal files (Markdown/TXT)
- Add optional resources/context
- **Real-time progress updates** showing which AI is working
- View vote breakdown and reasoning
- Download final proposals

### Command Line

```bash
# From a file
uv run python src/cli.py run --goal-file my_goal.md

# Direct text
uv run python src/cli.py run \
  --goal "Choose between FastAPI and Flask" \
  --resource "Team: 3 developers"

# Short flags
uv run python src/cli.py run -g "My goal" -r "Context" -o output.md
```

### Docker

```bash
# Build and run
make build-docker
make run-docker

# Access at http://localhost:8080
```

## Architecture

### The 4-Phase Process

1. **Phase 1 - Independent Ideation**
   - Each of 5 AIs independently proposes a solution
   - No cross-contamination to prevent anchoring bias
   - Progress shows: "Requesting proposal from Claude Opus 4.1..."

2. **Phase 2 - Peer Review**
   - All AIs review and critique each proposal
   - Identifies strengths, weaknesses, adoptable ideas
   - Progress shows: "Requesting critique from Llama 3.3 70B..."

3. **Phase 3 - Revision & Convergence**
   - Each AI creates refined V2 proposal
   - Incorporates best ideas from all proposals
   - Progress shows: "Requesting V2 proposal from Amazon Nova Pro..."

4. **Phase 4 - Ranked-Choice Vote**
   - Each AI ranks proposals (1st, 2nd, 3rd choice)
   - Point system: 1st choice = 3 pts, 2nd = 2 pts, 3rd = 1 pt
   - Self-voting disabled: councillors cannot rank their own proposals
   - Winner determined by total points
   - Progress shows: "Claude Sonnet 4: 1st=C (3pts), 2nd=A (2pts), 3rd=B (1pt)"

### Real-Time Progress

The web interface shows live updates:

```
[A] Requesting proposal from Amazon Nova Premier...
[A] ✓ Proposal received (4832 chars)
[B] Requesting proposal from Claude Sonnet 4...
[B] ✓ Proposal received (4156 chars)

[Memory] Total content: 23,456 characters
[Memory] Content under threshold. Skipping summarization.

Requesting critique from Amazon Nova Lite v2...
✓ Critique received from Amazon Nova Lite v2 (3421 chars)

✓ Amazon Nova Premier: 1st=C (3pts), 2nd=B (2pts), 3rd=D (1pt)
✓ Claude Sonnet 4: 1st=C (3pts), 2nd=A (2pts), 3rd=B (1pt)

RANKED-CHOICE VOTE TALLY (Points: 1st=3, 2nd=2, 3rd=1):
  Proposal C: 11 point(s)
  Proposal B: 7 point(s)
  Proposal A: 4 point(s)

🏆 WINNER: Proposal C with 11 points
```

### Key Improvements

**Ranked-Choice Voting System**
- Each councillor ranks 3 proposals instead of voting for just one
- Point allocation: 1st choice = 3 points, 2nd = 2 points, 3rd = 1 point
- Winner is determined by total points, providing more nuanced preferences
- Better represents councillor preferences and reduces impact of tactical voting

**Self-Voting Prevention**
- Councillors cannot vote for their own proposals
- Each councillor sees all proposals EXCEPT their own during voting
- Ensures fair evaluation and prevents bias toward own work
- Increases voting integrity and objectivity

**Smart Conditional Summarization**
- Summarization only activates when total content exceeds 50,000 characters
- For smaller debates (< 50K chars), full context is preserved
- Reduces API costs and maintains fidelity when possible
- When active, achieves 60-80% token reduction while preserving key information

## Project Structure

```
consilium/
├── .env.example            # Environment template
├── Dockerfile              # Container definition
├── Makefile                # Build automation
├── README.md               # This file
├── pyproject.toml          # Dependencies
├── pytest.ini              # Test configuration
├── src/
│   ├── cli.py              # CLI interface
│   ├── core.py             # Core debate logic
│   ├── web_app.py          # Gradio UI with real-time updates
│   ├── councillors/        # LLM agent implementations
│   ├── orchestrator/       # Debate coordination engine
│   └── memory/             # Context summarization
├── tests/                  # Test suite (37 tests)
└── output/                 # Generated proposals
```

## Example Use Cases

```
Technical Decisions:
- Choose between microservices vs monolith
- Select database (PostgreSQL, MongoDB, DynamoDB)
- Pick authentication method (JWT, OAuth2)

Architecture Design:
- Design API gateway for microservices
- Create caching strategy
- Plan database schema

Strategy & Planning:
- Prioritize features for MVP
- Choose tech stack
- Plan migration strategy
```

## Development

### Running Tests

```bash
make test                    # Run all tests
make test-cov               # With coverage
uv run pytest tests/ -v     # Verbose
```

**Results**: 37 passed, 10 skipped

### Makefile Commands

```bash
make help          # Show all commands
make install       # Install dependencies
make web-app       # Launch Gradio (PRIMARY)
make test          # Run tests
make build-docker  # Build Docker image
make run-docker    # Run in Docker
make clean         # Clean generated files
```

## Configuration

### Modify Councillors

Edit `src/orchestrator/engine.py`:

```python
self.councillors = [
    opus_councillor,        # Keep or replace
    nova_pro_councillor,   # Keep or replace
    # Add more councillors
]
```

### Adjust Summarization

Edit `src/memory/summarizer.py`:

```python
# Change summary length
prompt += "Keep under 300 words..."
```

### Progress Callback

Use progress tracking in your code:

```python
from orchestrator import Orchestrator

def my_callback(message):
    print(f"Progress: {message}")

orchestrator = Orchestrator(
    goal="My goal",
    progress_callback=my_callback
)
results = orchestrator.run()
```

## Performance

- **API Calls**: ~20-25 LLM invocations
- **Token Usage**: 150K-300K tokens (with summarization)
- **Memory Optimization**: 60-80% token reduction through intelligent summarization

## Docker

### Build

```bash
make build-docker
```

### Run

```bash
# Foreground
make run-docker

# Background
make run-docker-bg

# Stop
make stop-docker
```

### Custom

```bash
docker run -p 8080:8080 \
  --env-file .env \
  -v $(PWD)/output:/app/output \
  consilium:latest
```

## API Reference

```python
from core import run_debate, save_final_proposal

# Run with progress tracking
def my_progress(msg):
    print(f">> {msg}")

results = run_debate(
    goal="Choose a database...",
    resources="Additional context...",
    progress_callback=my_progress
)

# Save results
save_final_proposal(results, Path("output/proposal.md"))
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run `make test` to verify
5. Submit a pull request

## License

MIT License

## Acknowledgments

- **Inspiration**: [llm-council](https://github.com/karpathy/llm-council) by Andrej Karpathy
- Research foundations:
  - Society of Mind (Minsky)
  - LLM Debate frameworks
  - Multi-agent consensus systems
  - ChatEval evaluation protocols

## Support

- **Issues**: [GitHub Issues]
- **Tests**: `make test`
- **Help**: `uv run python src/cli.py --help`
