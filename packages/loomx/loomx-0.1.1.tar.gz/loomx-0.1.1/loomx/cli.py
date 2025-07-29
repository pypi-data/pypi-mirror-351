import click
from pathlib import Path

from .config import LoomxConfig
from .processor import LoomxProcessor
from .scanner import Scanner
from .parser import MarkdownParser


@click.group()
def cli():
    """loomx - Link and reference manager for markdown documentation."""
    pass


@cli.command()
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
@click.option("--verbose", is_flag=True, help="Verbose output")
@click.option(
    "--path",
    type=click.Path(exists=True, path_type=Path),
    default=".",
    help="Root path to scan",
)
def update(dry_run: bool, verbose: bool, path: Path):
    """Scan project and update @loomx metadata in markdown files."""
    config = LoomxConfig.from_pyproject(root_path=path, dry_run=dry_run, verbose=verbose)
    processor = LoomxProcessor(config)

    click.echo(f"Scanning for markdown files in {config.root_path}...")

    # Analyze all files first
    analysis = processor.analyze()
    total_files = len(list(processor.scanner.scan_files()))
    click.echo(f"Found {total_files} markdown files")

    # Get updates
    updates = processor.update_files()
    
    if config.verbose:
        for file_path, (references, backlinks) in analysis.items():
            click.echo(f"\nAnalyzing {file_path}:")
            click.echo(f"  References: {references}")
            click.echo(f"  Backlinks: {backlinks}")

    if config.dry_run:
        click.echo(f"\nDry run: Would update {len(updates)} files")
    else:
        click.echo(f"\nUpdated {len(updates)} files")


@cli.command()
@click.option(
    "--path",
    type=click.Path(exists=True, path_type=Path),
    default=".",
    help="Root path to check",
)
def check(path: Path):
    """Check for broken links in markdown files."""
    config = LoomxConfig.from_pyproject(root_path=path)
    scanner = Scanner(config)

    broken_links = []

    click.echo(f"Checking links in {config.root_path}...")

    for file_path in scanner.scan_files():
        parser = MarkdownParser(file_path)
        references = parser.extract_references()

        for ref in references:
            target_path = (file_path.parent / ref).resolve()
            if not target_path.exists():
                broken_links.append((file_path, ref))

    if broken_links:
        click.echo(f"\nFound {len(broken_links)} broken links:")
        for source, target in broken_links:
            click.echo(f"  {source} -> {target}")
    else:
        click.echo("\nNo broken links found!")


if __name__ == "__main__":
    cli()
