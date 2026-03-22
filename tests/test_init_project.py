import os
import shutil
import tempfile

import pytest

from scripts.init_project import (
    derive_names,
    validate_name,
    REPLACEMENTS,
    apply_replacements,
    rename_project,
    create_databases,
    reset_docs,
)


class TestValidateName:
    def test_valid_snake_case(self):
        assert validate_name("email_reviewer") is None

    def test_valid_single_word(self):
        assert validate_name("scraper") is None

    def test_valid_with_numbers(self):
        assert validate_name("app2") is None

    def test_rejects_empty(self):
        assert validate_name("") is not None

    def test_rejects_spaces(self):
        assert validate_name("my app") is not None

    def test_rejects_hyphens(self):
        assert validate_name("my-app") is not None

    def test_rejects_uppercase(self):
        assert validate_name("MyApp") is not None

    def test_rejects_leading_number(self):
        assert validate_name("2app") is not None

    def test_rejects_base_app(self):
        assert validate_name("base_app") is not None


class TestDeriveNames:
    def test_single_word(self):
        names = derive_names("scraper")
        assert names["snake"] == "scraper"
        assert names["kebab"] == "scraper"
        assert names["display"] == "Scraper"

    def test_two_words(self):
        names = derive_names("email_reviewer")
        assert names["snake"] == "email_reviewer"
        assert names["kebab"] == "email-reviewer"
        assert names["display"] == "Email Reviewer"

    def test_three_words(self):
        names = derive_names("brace_cost_scraper")
        assert names["snake"] == "brace_cost_scraper"
        assert names["kebab"] == "brace-cost-scraper"
        assert names["display"] == "Brace Cost Scraper"


class TestReplacements:
    def test_all_target_files_exist(self):
        """Every file listed in REPLACEMENTS must exist in the repo."""
        repo_root = os.path.dirname(os.path.dirname(__file__))
        for path, _ in REPLACEMENTS:
            full = os.path.join(repo_root, path)
            assert os.path.isfile(full), f"Missing: {path}"


class TestApplyReplacements:
    def test_replaces_all_forms_in_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text(
            "APP_NAME = 'Base App'\n"
            "DATABASE_URL = postgresql://localhost/base_app\n"
            "QUEUE_NAME = base-app\n"
        )
        names = derive_names("email_reviewer")
        apply_replacements(str(f), [("base_app", "snake"), ("base-app", "kebab"), ("Base App", "display")], names)
        content = f.read_text()
        assert "email_reviewer" in content
        assert "email-reviewer" in content
        assert "Email Reviewer" in content
        assert "base_app" not in content
        assert "base-app" not in content
        assert "Base App" not in content

    def test_leaves_unmatched_content_alone(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("This has nothing to replace.\n")
        names = derive_names("scraper")
        apply_replacements(str(f), [("base_app", "snake")], names)
        assert f.read_text() == "This has nothing to replace.\n"

    def test_handles_multiple_occurrences_per_line(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("base_app and base_app again\n")
        names = derive_names("scraper")
        apply_replacements(str(f), [("base_app", "snake")], names)
        assert f.read_text() == "scraper and scraper again\n"


class TestResetDocs:
    def test_readme_uses_project_name(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text("old content")
        names = derive_names("email_reviewer")
        reset_docs(str(tmp_path), names)
        content = readme.read_text()
        assert "# Email Reviewer" in content
        assert "base_app" not in content
        assert "install.sh" not in content
        assert "template" not in content.lower().replace("templates", "")

    def test_readme_has_dev_command(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text("old content")
        names = derive_names("email_reviewer")
        reset_docs(str(tmp_path), names)
        content = readme.read_text()
        assert "python manage.py dev" in content

    def test_readme_has_tech_stack(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text("old content")
        names = derive_names("email_reviewer")
        reset_docs(str(tmp_path), names)
        content = readme.read_text()
        assert "FastAPI" in content

    def test_development_md_no_template_section(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        dev_md = docs / "development.md"
        dev_md.write_text(
            "# Development\n\n"
            "## Prerequisites\n\n- Python 3.12\n\n"
            "## Initial Project Setup (from template)\n\n"
            "```bash\ncurl -sL https://example.com/install.sh | bash -s foo\n```\n\n"
            "This clones the repo.\n\n"
            "To run just the init step separately (e.g. if you already cloned manually):\n\n"
            "```bash\npython manage.py init foo\n```\n\n"
            "## Setup\n\n```bash\npython manage.py setup\n```\n"
        )
        names = derive_names("email_reviewer")
        reset_docs(str(tmp_path), names)
        content = dev_md.read_text()
        assert "## Prerequisites" in content
        assert "## Setup" in content
        assert "Initial Project Setup (from template)" not in content
        assert "install.sh" not in content

    def test_development_md_preserves_other_sections(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        dev_md = docs / "development.md"
        dev_md.write_text(
            "# Development\n\n"
            "## Prerequisites\n\n- Python 3.12\n\n"
            "## Initial Project Setup (from template)\n\ntemplate stuff\n\n"
            "## Setup\n\nsetup stuff\n\n"
            "## Running\n\nrunning stuff\n"
        )
        names = derive_names("email_reviewer")
        reset_docs(str(tmp_path), names)
        content = dev_md.read_text()
        assert "## Running" in content
        assert "running stuff" in content

    def test_skips_missing_development_md(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text("old")
        names = derive_names("scraper")
        reset_docs(str(tmp_path), names)
        assert readme.read_text() != "old"
