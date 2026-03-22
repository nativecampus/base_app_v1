#!/usr/bin/env python
"""Project management CLI. Run `python manage.py --help` for usage."""

import argparse
import os
import signal
import subprocess
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))

from scripts import init_project

WIZARD_INSTALL = "curl -sL https://raw.githubusercontent.com/nativecampus/claude-wizard/main/install.sh | bash"


def _run(cmd: list[str] | str, label: str, shell: bool = False) -> bool:
    """Run a command, print status, return True on success."""
    print(f"\n→ {label}")
    try:
        subprocess.run(cmd, check=True, cwd=_ROOT, shell=shell)
        return True
    except FileNotFoundError:
        print(f"  SKIP: command not found ({cmd[0] if isinstance(cmd, list) else cmd})")
        return False
    except subprocess.CalledProcessError:
        print("  FAILED")
        return False


def _install_deps() -> bool:
    return (
        _run(["pipenv", "install", "--dev"], "Installing Python dependencies")
        and _run(["npm", "install"], "Installing npm dependencies")
    )


def _create_databases(db_name: str) -> None:
    print("\n→ Creating databases")
    init_project.create_databases(db_name)


def _run_migrations() -> bool:
    return _run(["pipenv", "run", "alembic", "upgrade", "head"], "Running migrations")


def _build_css() -> bool:
    return _run(["npm", "run", "build:css"], "Building CSS")


def _install_wizard() -> bool:
    return _run(WIZARD_INSTALL, "Installing wizard skill", shell=True)


def _run_steps() -> bool:
    """Run the common setup steps. Returns False if any step fails."""
    if not _install_deps():
        return False
    if not _run_migrations():
        return False
    if not _build_css():
        return False
    _install_wizard()
    return True


def cmd_setup(_args: argparse.Namespace) -> None:
    """Set up the dev environment for working on the template itself."""
    _create_databases("base_app")
    if not _run_steps():
        sys.exit(1)
    print("\n✓ Setup complete. Run: python manage.py dev")


def cmd_init(args: argparse.Namespace) -> None:
    """Initialise a new project from the template."""
    error = init_project.validate_name(args.name)
    if error:
        print(f"Error: {error}")
        sys.exit(1)

    names = init_project.rename_project(args.name)

    if not args.no_db:
        print("\n→ Creating databases")
        init_project.create_databases(names["snake"])

    if not _run_steps():
        sys.exit(1)

    print(f"\n✓ {names['display']} is ready. Run: python manage.py dev")


def cmd_dev(_args: argparse.Namespace) -> None:
    """Run the dev server and CSS watcher."""
    css = subprocess.Popen(
        ["npm", "run", "watch:css"],
        cwd=_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    def _cleanup(signum, frame):
        css.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, _cleanup)
    signal.signal(signal.SIGTERM, _cleanup)

    print("Starting dev server (uvicorn + CSS watcher)...\n")
    try:
        server = subprocess.run(
            ["pipenv", "run", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
            cwd=_ROOT,
        )
        sys.exit(server.returncode)
    finally:
        css.terminate()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manage.py",
        description="Project management CLI for base_app.",
    )
    subs = parser.add_subparsers(dest="command")

    subs.add_parser("setup", help="Set up dev environment (install deps, create DB, migrate, build CSS)")

    init_p = subs.add_parser("init", help="Initialise a new project from the template")
    init_p.add_argument("name", help="Project name in snake_case (e.g. email_reviewer)")
    init_p.add_argument("--no-db", action="store_true", help="Skip database creation")

    subs.add_parser("dev", help="Run dev server + CSS watcher")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "setup":
        cmd_setup(args)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "dev":
        cmd_dev(args)


if __name__ == "__main__":
    main()
