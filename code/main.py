import click
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from code.config import DATASET_DIR, OUTPUT_DIR
from code.pipeline.orchestrator import process_dataset
from code.utils.logging import setup_logging
from code.evaluation.main import run_evaluation

console = Console()

@click.group()
def cli():
    pass

@cli.command()
@click.option("--claims", default=str(DATASET_DIR / "sample_claims.csv"))
@click.option("--history", default=str(DATASET_DIR / "user_history.csv"))
@click.option("--requirements", default=str(DATASET_DIR / "evidence_requirements.csv"))
@click.option("--output", default=str(OUTPUT_DIR / "output.csv"))
@click.option("--log-file", default="pipeline.log")
@click.option("--verbose", is_flag=True, help="Show detailed agent logs")
def run(claims, history, requirements, output, log_file, verbose):
    """Run the evidence review pipeline with progress display."""
    logger = setup_logging(log_file=Path(log_file))
    if verbose:
        logger.setLevel("DEBUG")
    logger.info("Starting pipeline")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Processing claims...", total=None)
        # process_dataset will write output.csv; we just run it
        process_dataset(Path(claims), Path(history), Path(requirements), Path(output))
        progress.update(task, completed=100)
    # Load output and show summary table
    df = pd.read_csv(output)
    table = Table(title="Pipeline Summary")
    table.add_column("User ID", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Issue", style="yellow")
    for _, row in df.iterrows():
        table.add_row(row["user_id"], row["claim_status"], row["issue_type"])
    console.print(table)

@cli.command()
@click.option("--claims", default=str(DATASET_DIR / "sample_claims.csv"))
@click.option("--history", default=str(DATASET_DIR / "user_history.csv"))
@click.option("--requirements", default=str(DATASET_DIR / "evidence_requirements.csv"))
@click.option("--output-predictions", default=str(OUTPUT_DIR / "eval_predictions.csv"))
@click.option("--report", default=str(Path("evaluation") / "report.md"))
def evaluate(claims, history, requirements, output_predictions, report):
    """Run evaluation on sample claims."""
    run_evaluation(
        claims=Path(claims),
        history=Path(history),
        requirements=Path(requirements),
        output_predictions=Path(output_predictions),
        report=Path(report),
    )

if __name__ == "__main__":
    cli()