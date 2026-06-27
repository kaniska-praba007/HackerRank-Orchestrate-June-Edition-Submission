"""Evaluation runner – compares pipeline predictions to ground truth."""
import click
import pandas as pd
from pathlib import Path
from code.pipeline.orchestrator import process_dataset
from code.config import DATASET_DIR, OUTPUT_DIR
from code.utils.logging import setup_logging

# Columns we can directly compare (exact match)
ACCURACY_COLUMNS = [
    "claim_status",
    "issue_type",
    "object_part",
    "severity",
]

def run_pipeline_and_load_predictions(claims_csv: Path, history_csv: Path,
                                      req_csv: Path, output_csv: Path) -> pd.DataFrame:
    """Execute the pipeline and return the output as a DataFrame."""
    process_dataset(claims_csv, history_csv, req_csv, output_csv)
    return pd.read_csv(output_csv).set_index("user_id")

def load_ground_truth(claims_csv: Path) -> pd.DataFrame:
    """Load sample claims CSV and keep the ground truth columns."""
    df = pd.read_csv(claims_csv)
    df["user_id"] = df["user_id"].astype(str)
    return df.set_index("user_id")

def compute_metrics(pred: pd.DataFrame, gt: pd.DataFrame) -> dict:
    """Compare predictions against ground truth for selected columns."""
    common = pred.index.intersection(gt.index)
    pred = pred.loc[common]
    gt = gt.loc[common]
    metrics = {}

    for col in ACCURACY_COLUMNS:
        if col in pred.columns and col in gt.columns:
            # Normalise strings: lower, strip
            p = pred[col].astype(str).str.lower().str.strip()
            g = gt[col].astype(str).str.lower().str.strip()
            correct = (p == g).sum()
            metrics[f"{col}_accuracy"] = correct / len(common) if len(common) > 0 else 0.0

    # Evidence standard met (boolean/string)
    if "evidence_standard_met" in pred.columns and "evidence_standard_met" in gt.columns:
        p = pred["evidence_standard_met"].astype(str).str.lower().str.strip()
        g = gt["evidence_standard_met"].astype(str).str.lower().str.strip()
        correct = (p == g).sum()
        metrics["evidence_standard_met_accuracy"] = correct / len(common) if len(common) > 0 else 0.0

    # Risk flags (compare sets, order agnostic)
    if "risk_flags" in pred.columns and "risk_flags" in gt.columns:
        def to_set(flags_str):
            if pd.isna(flags_str) or flags_str.strip() == "":
                return frozenset()
            return frozenset(f.strip() for f in flags_str.split(";"))
        p_sets = pred["risk_flags"].apply(to_set)
        g_sets = gt["risk_flags"].apply(to_set)
        correct = (p_sets == g_sets).sum()
        metrics["risk_flags_accuracy"] = correct / len(common) if len(common) > 0 else 0.0

    return metrics, pred, gt

def generate_report(metrics: dict, pred: pd.DataFrame, gt: pd.DataFrame, report_path: Path):
    """Write markdown report with metrics and error details."""
    lines = ["# Evaluation Report", ""]
    lines.append("## Accuracy Metrics")
    for k, v in metrics.items():
        lines.append(f"- **{k}**: {v:.2%}")
    lines.append("")

    lines.append("## Error Analysis")
    lines.append("")

    # Show claim status mismatches
    if "claim_status" in pred.columns and "claim_status" in gt.columns:
        lines.append("### Claim Status Discrepancies")
        mismatched = (pred["claim_status"] != gt["claim_status"])
        for uid in pred.index[mismatched]:
            lines.append(f"- **{uid}**: predicted `{pred.loc[uid, 'claim_status']}` "
                         f"but expected `{gt.loc[uid, 'claim_status']}`")
        lines.append("")

    # Show issue type mismatches
    if "issue_type" in pred.columns and "issue_type" in gt.columns:
        lines.append("### Issue Type Discrepancies")
        mismatched = (pred["issue_type"] != gt["issue_type"])
        for uid in pred.index[mismatched]:
            lines.append(f"- **{uid}**: predicted `{pred.loc[uid, 'issue_type']}` "
                         f"but expected `{gt.loc[uid, 'issue_type']}`")
        lines.append("")

    # Similarly for object_part, severity, evidence_standard_met, risk_flags...
    # Add as needed.

    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")

def run_evaluation(claims: Path, history: Path, requirements: Path,
                   output_predictions: Path, report: Path):
    """Core evaluation logic, callable from other modules."""
    logger = setup_logging()
    logger.info("Starting evaluation...")

    # 1. Run pipeline to produce predictions
    logger.info("Running pipeline...")
    pred_df = run_pipeline_and_load_predictions(
        claims, history, requirements, output_predictions
    )
    logger.info(f"Predictions loaded: {len(pred_df)} rows")

    # 2. Load ground truth
    gt_df = load_ground_truth(claims)
    logger.info(f"Ground truth loaded: {len(gt_df)} rows")

    # 3. Compute metrics
    metrics, pred_aligned, gt_aligned = compute_metrics(pred_df, gt_df)
    logger.info("Metrics computed")

    # 4. Generate report
    generate_report(metrics, pred_aligned, gt_aligned, report)
    logger.info(f"Report written to {report}")

    # Print summary
    click.echo("Evaluation complete. Metrics:")
    for k, v in metrics.items():
        click.echo(f"  {k}: {v:.2%}")

@click.command()
@click.option("--claims", default=str(DATASET_DIR / "sample_claims.csv"))
@click.option("--history", default=str(DATASET_DIR / "user_history.csv"))
@click.option("--requirements", default=str(DATASET_DIR / "evidence_requirements.csv"))
@click.option("--output-predictions", default=str(OUTPUT_DIR / "eval_predictions.csv"))
@click.option("--report", default=str(Path("evaluation") / "report.md"))
def evaluate(claims, history, requirements, output_predictions, report):
    """CLI entry point for evaluation."""
    run_evaluation(
        claims=Path(claims),
        history=Path(history),
        requirements=Path(requirements),
        output_predictions=Path(output_predictions),
        report=Path(report),
    )
    
if __name__ == "__main__":
    evaluate()