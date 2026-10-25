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
