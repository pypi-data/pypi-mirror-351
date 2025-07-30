"""Project commands: runserver, migrate, createsuperuser."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Optional

import click

PROJECT_MARKER = ".prompta_project"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_project_root(start: Path | None = None) -> Path:
    """Ascend directories until we find `.prompta_project` marker."""

    current = start or Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / PROJECT_MARKER).is_file():
            return parent
    raise click.ClickException("This command must be run inside a Prompta project directory.")


def _ensure_on_sys_path(path: Path) -> None:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


# ---------------------------------------------------------------------------
# runserver
# ---------------------------------------------------------------------------


@click.command("runserver")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True, type=int)
@click.option("--reload/--no-reload", default=True, show_default=True)
def runserver_command(host: str, port: int, reload: bool) -> None:  # pragma: no cover
    """Start the FastAPI development server (uvicorn)."""

    project_root = _find_project_root()
    _ensure_on_sys_path(project_root)

    try:
        import uvicorn  # pylint: disable=import-error

        from importlib import import_module

        # Import the FastAPI instance
        app_module = import_module("app.main")
        app = getattr(app_module, "app", None)
        if app is None:
            raise click.ClickException("Could not find FastAPI `app` in app.main")

        uvicorn.run(app, host=host, port=port, reload=reload)

    except ModuleNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc


# ---------------------------------------------------------------------------
# migrate
# ---------------------------------------------------------------------------


@click.command("migrate")
@click.option(
    "--autogenerate",
    is_flag=True,
    help="Autogenerate migration (alembic revision --autogenerate).",
)
@click.option("-m", "--message", default="auto", help="Migration message.")
def migrate_command(autogenerate: bool, message: str) -> None:  # pragma: no cover
    """Run database migrations (Alembic)."""

    project_root = _find_project_root()
    _ensure_on_sys_path(project_root)

    try:
        from alembic import command as alembic_cmd  # pylint: disable=import-error
        from alembic.config import Config as AlembicConfig

        alembic_ini = project_root / "alembic.ini"
        if not alembic_ini.exists():
            raise click.ClickException("Could not find alembic.ini in project root")

        cfg = AlembicConfig(str(alembic_ini))

        if autogenerate:
            click.echo("🔄 Generating new migration …")
            alembic_cmd.revision(cfg, autogenerate=True, message=message)
        else:
            click.echo("📜 Applying migrations …")
            alembic_cmd.upgrade(cfg, "head")

    except ModuleNotFoundError as exc:
        raise click.ClickException(
            "Alembic is not installed – add it to your environment: pip install alembic"
        ) from exc


# ---------------------------------------------------------------------------
# createsuperuser
# ---------------------------------------------------------------------------


@click.command("createsuperuser")
def createsuperuser_command() -> None:  # pragma: no cover
    """Interactive creation of an admin user."""

    project_root = _find_project_root()
    _ensure_on_sys_path(project_root)

    import getpass

    # Lazy imports (inside project environment)
    from sqlalchemy.exc import IntegrityError

    try:
        from app.database import SessionLocal, create_tables  # type: ignore

        # Import models to satisfy SQLAlchemy relationship resolution before using
        # the User class (it references Prompt via relationship()).
        import prompts.models  # type: ignore  # noqa: F401
        from auth.models import User  # type: ignore
        from auth.security import get_password_hash  # type: ignore
    except ModuleNotFoundError as exc:
        raise click.ClickException(
            "Failed to import project modules – are you in a Prompta project directory?"
        ) from exc

    # Ensure tables exist
    create_tables()

    username = click.prompt("Username")
    email = click.prompt("Email")

    while True:
        pwd1 = getpass.getpass("Password: ")
        pwd2 = getpass.getpass("Password (again): ")
        if pwd1 != pwd2:
            click.echo("Passwords don't match. Try again.")
            continue
        if len(pwd1) < 6:
            click.echo("Password must be at least 6 characters long.")
            continue
        break

    db = SessionLocal()
    import hashlib

    try:
        # get_password_hash uses Passlib (bcrypt). Fallback to sha256 if bcrypt backend
        # is unavailable in the current environment so the command still works for
        # quick local testing.
        try:
            hashed = get_password_hash(pwd1)
        except Exception:  # pragma: no cover
            click.echo("⚠️  bcrypt backend not available – using SHA256 hash.")
            hashed = hashlib.sha256(pwd1.encode()).hexdigest()

        user = User(username=username, email=email, password_hash=hashed, is_active=True)
        db.add(user)
        db.commit()
        click.echo("✅ Superuser created successfully")
    except IntegrityError:
        db.rollback()
        raise click.ClickException("User with that username or email already exists")
    finally:
        db.close()


# Convenience accessor for adding all commands from other modules
commands = [runserver_command, migrate_command, createsuperuser_command]
