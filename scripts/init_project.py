"""Initialise a new project from the base app template.

Usage: python -m scripts.init_project <project_name>

project_name must be snake_case (e.g. email_reviewer, brace_scraper).
The script renames all references to base_app/base-app/Base App throughout
the codebase, then optionally creates the local databases.
"""

import os
import re
import subprocess
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (file_path_relative_to_repo, [(old_text, name_form), ...])
# name_form is one of: "snake", "kebab", "display"
REPLACEMENTS: list[tuple[str, list[tuple[str, str]]]] = [
    ("app/config.py", [("Base App", "display"), ("base_app", "snake")]),
    ("app/worker.py", [("base-app", "kebab")]),
    (".env.example", [("base_app", "snake")]),
    ("Procfile", [("base-app", "kebab")]),
    ("alembic.ini", [("base_app", "snake")]),
    ("pytest.ini", [("base_app", "snake")]),
    ("CLAUDE.md", [("base_app", "snake")]),
    ("README.md", [("Base App", "display"), ("base_app", "snake"), ("base-app", "kebab")]),
    ("docs/development.md", [("base_app", "snake"), ("base-app", "kebab")]),
    ("docs/testing-guide.md", [("base_app", "snake")]),
    ("app/templates/base.html", [("Base App", "display")]),
    ("app/templates/index.html", [("base app", "display_lower")]),
    (".github/workflows/ci.yml", [("base_app", "snake")]),
    ("package.json", [("base_app", "snake")]),
]


def validate_name(name: str) -> str | None:
    """Return an error message if the name is invalid, else None."""
    if not name:
        return "Name cannot be empty"
    if name == "base_app":
        return "Pick a real name, not 'base_app'"
    if not re.match(r"^[a-z][a-z0-9_]*$", name):
        return "Name must be snake_case: lowercase letters, digits, underscores, starting with a letter"
    return None


def derive_names(snake: str) -> dict[str, str]:
    """Derive all name forms from a snake_case name."""
    return {
        "snake": snake,
        "kebab": snake.replace("_", "-"),
        "display": snake.replace("_", " ").title(),
        "display_lower": snake.replace("_", " "),
    }


def apply_replacements(
    filepath: str,
    replacements: list[tuple[str, str]],
    names: dict[str, str],
) -> None:
    """Replace all occurrences in a single file."""
    with open(filepath) as f:
        content = f.read()
    for old_text, name_form in replacements:
        content = content.replace(old_text, names[name_form])
    with open(filepath, "w") as f:
        f.write(content)


def run(name: str, *, auto_yes: bool = False) -> None:
    names = derive_names(name)

    print(f"Renaming project to: {names['display']} ({names['snake']})")

    for relpath, repls in REPLACEMENTS:
        filepath = os.path.join(_REPO_ROOT, relpath)
        if not os.path.isfile(filepath):
            print(f"  SKIP {relpath} (not found)")
            continue
        apply_replacements(filepath, repls, names)
        print(f"  {relpath}")

    print()
    if auto_yes:
        answer = "y"
    else:
        print(f"Create databases now? (createdb {names['snake']} && createdb -U test {names['snake']}_test)")
        answer = input("[Y/n] ").strip().lower()
    if answer in ("", "y", "yes"):
        for cmd in [
            ["createdb", names["snake"]],
            ["createdb", "-U", "test", f"{names['snake']}_test"],
        ]:
            try:
                subprocess.run(cmd, check=True)
                print(f"  Created: {cmd[-1]}")
            except subprocess.CalledProcessError:
                print(f"  Already exists or failed: {cmd[-1]}")
    else:
        print("  Skipped. Create them manually when ready.")

    print()
    print("Done. Next steps:")
    print(f"  1. pipenv install --dev")
    print(f"  2. pipenv run alembic upgrade head")
    print(f"  3. Add your models, then: pipenv run alembic revision --autogenerate -m 'initial tables'")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    flags = {a for a in sys.argv[1:] if a.startswith("-")}

    if len(args) != 1:
        print("Usage: python -m scripts.init_project [--yes] <project_name>")
        print("  project_name: snake_case (e.g. email_reviewer)")
        print("  --yes: skip confirmation prompts")
        sys.exit(1)

    name = args[0]
    error = validate_name(name)
    if error:
        print(f"Error: {error}")
        sys.exit(1)

    run(name, auto_yes="--yes" in flags)


if __name__ == "__main__":
    main()
