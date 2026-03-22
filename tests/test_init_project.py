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
