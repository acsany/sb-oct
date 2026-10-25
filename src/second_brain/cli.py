"""CLI entry point using Click."""

from __future__ import annotations

import click
from loguru import logger

from second_brain.app import configure_logging
from second_brain.notes import create_note, notes_dir


@click.group()
def cli():
    """second_brain -- capture and organise your thoughts."""
    configure_logging()


@cli.command()
@click.argument("title")
def new(title: str):
    """Create a new note with the given TITLE."""
    base_dir = notes_dir()
    logger.debug("Creating note in {}", base_dir)
    path = create_note(title, base_dir)
    logger.info("Created note: {}", path)
    click.echo(path)


@cli.command("list")
def list_notes():
    """List all notes in the notes directory."""
    base_dir = notes_dir()

    if not base_dir.is_dir():
        logger.warning("Notes directory does not exist: {}", base_dir)
        click.echo(f"Notes directory does not exist: {base_dir}")
        return

    files = sorted(base_dir.glob("*.md"), reverse=True)

    click.echo(f"Notes: {base_dir}")

    if not files:
        logger.info("No notes found in {}", base_dir)
        click.echo("No notes found.")
        return

    logger.debug("Found {} note(s) in {}", len(files), base_dir)
    for i, f in enumerate(files, 1):
        click.echo(f"{i}. {f.name}")
