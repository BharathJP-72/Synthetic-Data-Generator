"""
Synthetic-Data-Generator CLI – Mimesis edition
"""
import click, json, pandas as pd
from pathlib import Path
from src.core.engine import SyntheticDataEngine
from src.generators.mimesis_generator import MimesisGenerator
from src.exporters.csv_exporter import CSVExporter
from src.exporters.json_exporter import JSONExporter
from src.exporters.excel_exporter import ExcelExporter


@click.group()
def cli():
    """High-quality synthetic data via Mimesis."""


@cli.command()
@click.option("--prompt", "-p", required=True)
@click.option("--rows", "-r", default=1000)
@click.option("--output", "-o", default="output.csv")
@click.option("--format", "output_format", default="csv",
              type=click.Choice(["csv", "json", "excel"]))
def prompt_based(prompt: str, rows: int, output: str, output_format: str):
    engine = SyntheticDataEngine()
    engine.register_generator("mimesis", MimesisGenerator())
    exporter = {"csv": CSVExporter(), "json": JSONExporter(), "excel": ExcelExporter()}[output_format]
    data = engine.generate_from_prompt(prompt, rows, output_format)
    exporter.export(data, output)
    click.echo(f"✅  Generated {rows} rows → {output}")


@cli.command()
@click.option("--file", "-f", required=True)
@click.option("--rows", "-r", default=1000)
@click.option("--output", "-o", default="synthetic.csv")
@click.option("--format", "output_format", default="csv",
              type=click.Choice(["csv", "json", "excel"]))
@click.option("--preserve-stats/--no-preserve-stats", default=True)
def file_based(file: str, rows: int, output: str, output_format: str, preserve_stats: bool):
    engine = SyntheticDataEngine()
    engine.register_generator("mimesis", MimesisGenerator())
    exporter = {"csv": CSVExporter(), "json": JSONExporter(), "excel": ExcelExporter()}[output_format]
    data = engine.generate_from_file(file, rows, preserve_stats, output_format)
    exporter.export(data, output)
    click.echo(f"✅  Generated {rows} rows → {output}")


@cli.command()
@click.option("--config-file", "-c", required=True)
def batch_generate(config_file: str):
    cfg = json.loads(Path(config_file).read_text())
    engine = SyntheticDataEngine()
    engine.register_generator("mimesis", MimesisGenerator())
    results = engine.batch_generate(cfg["requests"])
    out_dir = Path(cfg.get("output_directory", "batch_output"))
    out_dir.mkdir(exist_ok=True)
    for i, (req, df) in enumerate(zip(cfg["requests"], results)):
        fmt = req.get("output_format", "csv")
        exporter = {"csv": CSVExporter(), "json": JSONExporter(), "excel": ExcelExporter()}[fmt]
        exporter.export(df, out_dir / f"dataset_{i+1}.{fmt}")
    click.echo(f"✅  Batch complete → {out_dir}")


# ------------------------------------------------------------------
# NEW COMMAND – place HERE (above the bottom if-block)
# ------------------------------------------------------------------
@cli.command()
@click.option("--schema", "-s", required=True, help="JSON schema file")
@click.option("--rows", "-r", default=10)
@click.option("--output", "-o", default="direct.csv")
def from_schema(schema: str, rows: int, output: str):
    """Generate from explicit JSON schema."""
    engine = SyntheticDataEngine()
    engine.register_generator("mimesis", MimesisGenerator())

    with open(schema) as f:
        schema_dict = json.load(f)

    data = engine._generate_from_schema(schema_dict, rows)
    data.to_csv(output, index=False)
    click.echo(f"✅  Generated {rows} rows → {output}")

@cli.command()
def interactive():
    """Ask user for prompt, rows, file name and generate."""
    print("\n🚀  Interactive Synthetic-Data Generator (Mimesis)\n")
    prompt  = input("📄  Describe the data you need  : ").strip()
    rows    = int(input("🔢  Number of rows             : ").strip())
    out     = input("💾  Output file name (.csv)    : ").strip() or "output.csv"
    if not out.endswith(".csv"):
        out += ".csv"

    engine = SyntheticDataEngine()
    engine.register_generator("mimesis", MimesisGenerator())
    data = engine.generate_from_prompt(prompt, rows)
    CSVExporter().export(data, out)
    print(f"\n✅  Generated {rows} realistic rows → {Path(out).absolute()}\n")


if __name__ == "__main__":
    cli()

