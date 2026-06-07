"""Database migration utilities and management."""

import subprocess
import sys
from pathlib import Path

import click


@click.group()
def cli():
    """Database migration management."""
    pass


@cli.command()
def init():
    """Initialize database migrations."""
    click.echo("Initializing Alembic...")
    subprocess.run([sys.executable, "-m", "alembic", "init", "migrations"], check=True)
    click.echo("✅ Alembic initialized")


@cli.command()
@click.option(
    "--message",
    "-m",
    required=True,
    help="Migration description",
)
def revision(message: str):
    """Create new migration."""
    click.echo(f"Creating migration: {message}")
    subprocess.run(
        [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", message],
        check=True,
    )
    click.echo(f"✅ Migration created: {message}")


@cli.command()
@click.option(
    "--revision",
    "-r",
    default="head",
    help="Target revision (default: head)",
)
def upgrade(revision: str):
    """Apply migrations."""
    click.echo(f"Applying migrations to {revision}...")
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", revision],
        check=True,
    )
    click.echo(f"✅ Migrations applied to {revision}")


@cli.command()
@click.option(
    "--revision",
    "-r",
    default="-1",
    help="Target revision (default: -1, rollback one)",
)
def downgrade(revision: str):
    """Rollback migrations."""
    click.echo(f"Rolling back migrations to {revision}...")
    subprocess.run(
        [sys.executable, "-m", "alembic", "downgrade", revision],
        check=True,
    )
    click.echo(f"✅ Migrations rolled back to {revision}")


@cli.command()
def history():
    """Show migration history."""
    click.echo("Migration history:")
    subprocess.run(
        [sys.executable, "-m", "alembic", "history"],
        check=True,
    )


@cli.command()
def current():
    """Show current migration."""
    click.echo("Current migration:")
    subprocess.run(
        [sys.executable, "-m", "alembic", "current"],
        check=True,
    )


if __name__ == "__main__":
    cli()
