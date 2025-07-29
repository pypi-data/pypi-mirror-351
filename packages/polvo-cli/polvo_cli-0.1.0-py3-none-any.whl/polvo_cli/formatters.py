from rich.console import Console
from rich.table import Table
from typing import Dict, Any
import csv
import sys

console = Console()


def format_results(results: Dict[str, Any], format: str = "table"):
    """Format and display evaluation results."""
    if format == "table":
        # Main results table
        table = Table(title="Embedding Model Evaluation Results")
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Retrieval", justify="right")
        table.add_column("Clustering", justify="right")
        table.add_column("Speed (ms)", justify="right")
        table.add_column("Cost/1K", justify="right")
        table.add_column("Dims", justify="right")

        # Add rows
        for model, metrics in results['results'].items():
            retrieval = f"{metrics['retrieval_score']:.2f}"
            clustering = f"{metrics['clustering_score']:.2f}"
            speed = f"{metrics['speed_ms']:.0f}"
            cost = f"${metrics['cost_per_1k']}" if metrics['cost_per_1k'] > 0 else "Free"
            dims = str(metrics['dimensions'])

            style = "bold green" if metrics.get('recommended') else None
            table.add_row(model, retrieval, clustering, speed, cost, dims, style=style)

        console.print(table)

        # Recommendations
        console.print("\n[bold]Recommendations:[/bold]")
        for rec in results['recommendations']:
            console.print(f"  {rec}")

        # Best model
        console.print(f"\n[bold green]Best model: {results['best_model']}[/bold green]")

    elif format == "csv":
        writer = csv.DictWriter(
            sys.stdout,
            fieldnames=['model', 'retrieval_score', 'clustering_score',
                       'speed_ms', 'cost_per_1k', 'dimensions']
        )
        writer.writeheader()

        for model, metrics in results['results'].items():
            writer.writerow({
                'model': model,
                'retrieval_score': metrics['retrieval_score'],
                'clustering_score': metrics['clustering_score'],
                'speed_ms': metrics['speed_ms'],
                'cost_per_1k': metrics['cost_per_1k'],
                'dimensions': metrics['dimensions']
            })


def format_models(models_data: Dict[str, Any]):
    """Format and display available models."""
    table = Table(title="Available Embedding Models")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Provider", style="magenta")
    table.add_column("Model Name")
    table.add_column("Description", style="dim")

    for model in models_data['models']:
        table.add_row(
            model['key'],
            model['provider'],
            model['model_name'],
            model['description']
        )

    console.print(table)
    console.print(f"\nTotal models available: {models_data['count']}") 