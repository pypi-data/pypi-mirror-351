import click
from pathlib import Path

from .config import LoomxConfig
from .scanner import Scanner
from .parser import MarkdownParser
from .graph import LinkGraph
from .formatter import LoomxFormatter


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

    # Initialize components
    scanner = Scanner(config)
    graph = LinkGraph(root_path=config.root_path)
    formatter = LoomxFormatter()

    click.echo(f"Scanning for markdown files in {config.root_path}...")

    # First pass: build the graph
    files_found = []
    for file_path in scanner.scan_files():
        files_found.append(file_path)
        parser = MarkdownParser(file_path)
        found_references = parser.extract_references()

        if config.verbose:
            click.echo(f"Found {len(found_references)} references in {file_path}")

        graph.add_references(file_path, found_references)

    click.echo(f"Found {len(files_found)} markdown files")

    # Second pass: update files with metadata
    updated_count = 0
    for file_path in files_found:
        references_list = graph.get_references(file_path)
        backlinks_list = graph.get_backlinks(file_path)

        if references_list or backlinks_list:
            if config.verbose:
                click.echo(f"\nUpdating {file_path}:")
                click.echo(f"  References: {references_list}")
                click.echo(f"  Backlinks: {backlinks_list}")

            if not config.dry_run:
                original_content = file_path.read_text(encoding="utf-8")
                updated_content = formatter.update_file(
                    file_path, references_list, backlinks_list
                )
                
                # Only write and count if content actually changed
                if original_content != updated_content:
                    file_path.write_text(updated_content, encoding="utf-8")
                    updated_count += 1
            else:
                # For dry run, we assume it would update
                updated_count += 1

    if config.dry_run:
        click.echo(f"\nDry run: Would update {updated_count} files")
    else:
        click.echo(f"\nUpdated {updated_count} files")


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
