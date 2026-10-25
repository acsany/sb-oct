"""CLI entry point using Click."""

from __future__ import annotations

import click
from loguru import logger

from second_brain.app import configure_logging
from second_brain.notes import create_note, list_note_files, notes_dir, read_note


@click.group()
def cli():
    """second_brain -- capture and organise your thoughts."""
    configure_logging()


@cli.command()
@click.argument("title")
@click.option(
    "--body",
    "-b",
    help="Note body (multi-line). Use '-' to read it from stdin.",
)
def new(title: str, body: str | None):
    """Create a new note with the given TITLE.

    If TITLE contains newlines, the first line becomes the heading and the rest
    is added to the note body.
    """
    if body == "-":
        with click.open_file("-", encoding="utf-8") as stdin:
            body = stdin.read()
    base_dir = notes_dir()
    logger.debug("Creating note in {}", base_dir)
    path = create_note(title, base_dir, body=body)
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

    files = list_note_files(base_dir)

    click.echo(f"Notes: {base_dir}")

    if not files:
        logger.info("No notes found in {}", base_dir)
        click.echo("No notes found.")
        return

    logger.debug("Found {} note(s) in {}", len(files), base_dir)
    for i, f in enumerate(files, 1):
        click.echo(f"{i}. {f.name}")


@cli.command()
@click.argument("number", type=int)
def show(number: int):
    """Display the contents of note NUMBER."""
    base_dir = notes_dir()

    if not base_dir.is_dir():
        logger.error("Notes directory does not exist: {}", base_dir)
        click.echo(f"Error: Notes directory does not exist: {base_dir}", err=True)
        raise SystemExit(1)

    files = list_note_files(base_dir)

    if not files:
        logger.error("No notes found in {}", base_dir)
        click.echo("Error: No notes found.", err=True)
        raise SystemExit(1)

    if number < 1 or number > len(files):
        logger.error("Note {} out of range ({} available)", number, len(files))
        click.echo(
            f"Error: Note {number} not found. Only {len(files)} notes available.",
            err=True,
        )
        raise SystemExit(1)

    logger.debug("Showing note {}: {}", number, files[number - 1].name)
    click.echo(read_note(files[number - 1]))
