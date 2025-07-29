import typer
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import sys

from .client import PolvoClient
from .formatters import format_results, format_models
from .config import get_api_url

app = typer.Typer(
    name="polvo",
    help="🐙 Polvo CLI - Find the best embedding model for your data",
    add_completion=False,
)
console = Console()


@app.command()
def test(
    file: Path = typer.Argument(..., help="Dataset file (CSV, JSON, or TXT)"),
    models: List[str] = typer.Option(
        ["minilm", "mpnet"],
        "--model", "-m",
        help="Models to test (can specify multiple)"
    ),
    column: Optional[str] = typer.Option(
        None, "--column", "-c",
        help="Column name for CSV files"
    ),
    output: str = typer.Option(
        "table", "--output", "-o",
        help="Output format: table, json, csv"
    ),
    api_url: Optional[str] = typer.Option(
        None, "--api-url",
        help="API URL (default: http://localhost:8000)"
    ),
):
    """Test embedding models on your dataset."""
    client = PolvoClient(api_url or get_api_url())

    # Check file exists
    if not file.exists():
        console.print(f"[red]Error: File '{file}' not found[/red]")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Upload file
        task = progress.add_task("Uploading dataset...", total=None)
        try:
            upload_result = client.upload_file(file)
            progress.update(task, description=f"Uploaded {upload_result['count']} texts")
        except Exception as e:
            console.print(f"[red]Upload failed: {e}[/red]")
            raise typer.Exit(1)

        # Evaluate models
        progress.update(task, description=f"Testing {len(models)} models...")
        try:
            results = client.evaluate(
                texts=upload_result['texts'],
                models=models
            )
            progress.update(task, description="Evaluation complete!")
        except Exception as e:
            console.print(f"[red]Evaluation failed: {e}[/red]")
            raise typer.Exit(1)

    # Format and display results
    if output == "json":
        import json
        console.print(json.dumps(results, indent=2))
    elif output == "csv":
        format_results(results, format="csv")
    else:
        format_results(results, format="table")


@app.command()
def models(
    api_url: Optional[str] = typer.Option(
        None, "--api-url",
        help="API URL (default: http://localhost:8000)"
    ),
):
    """List available embedding models."""
    client = PolvoClient(api_url or get_api_url())

    try:
        models = client.get_models()
        format_models(models)
    except Exception as e:
        console.print(f"[red]Failed to fetch models: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def health(
    api_url: Optional[str] = typer.Option(
        None, "--api-url",
        help="API URL (default: http://localhost:8000)"
    ),
):
    """Check API health status."""
    client = PolvoClient(api_url or get_api_url())

    try:
        status = client.health_check()
        console.print(f"✅ API is [green]healthy[/green]")
        console.print(f"Service: {status.get('service', 'unknown')}")
    except Exception as e:
        console.print(f"❌ API is [red]unhealthy[/red]: {e}")
        raise typer.Exit(1)


@app.command()
def version():
    """Show CLI version."""
    console.print("Polvo CLI v0.1.0")


if __name__ == "__main__":
    app() 