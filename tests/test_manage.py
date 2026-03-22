import subprocess
from unittest.mock import patch, call, MagicMock

import pytest

from manage import build_parser, main, cmd_setup, cmd_init, cmd_dev, _run


class TestBuildParser:
    def test_setup_command(self):
        args = build_parser().parse_args(["setup"])
        assert args.command == "setup"

    def test_init_command_with_name(self):
        args = build_parser().parse_args(["init", "my_app"])
        assert args.command == "init"
        assert args.name == "my_app"

    def test_init_no_db_flag(self):
        args = build_parser().parse_args(["init", "my_app", "--no-db"])
        assert args.no_db is True

    def test_init_default_db(self):
        args = build_parser().parse_args(["init", "my_app"])
        assert args.no_db is False

    def test_dev_command(self):
        args = build_parser().parse_args(["dev"])
        assert args.command == "dev"

    def test_no_command_sets_none(self):
        args = build_parser().parse_args([])
        assert args.command is None


class TestMain:
    def test_no_command_exits(self):
        with pytest.raises(SystemExit) as exc:
            main([])
        assert exc.value.code == 1

    def test_dispatches_to_setup(self):
        with patch("manage.cmd_setup") as mock:
            main(["setup"])
            mock.assert_called_once()

    def test_dispatches_to_init(self):
        with patch("manage.cmd_init") as mock:
            main(["init", "my_app"])
            mock.assert_called_once()

    def test_dispatches_to_dev(self):
        with patch("manage.cmd_dev") as mock:
            main(["dev"])
            mock.assert_called_once()


class TestRun:
    def test_successful_command(self):
        with patch("manage.subprocess.run") as mock_run:
            result = _run(["echo", "hi"], "test")
            assert result is True
            mock_run.assert_called_once()

    def test_failed_command(self):
        with patch("manage.subprocess.run", side_effect=subprocess.CalledProcessError(1, "fail")):
            result = _run(["fail"], "test")
            assert result is False

    def test_missing_command(self):
        with patch("manage.subprocess.run", side_effect=FileNotFoundError):
            result = _run(["nonexistent"], "test")
            assert result is False


class TestCmdSetup:
    @patch("manage._install_wizard", return_value=True)
    @patch("manage._build_css", return_value=True)
    @patch("manage._run_migrations", return_value=True)
    @patch("manage._create_databases")
    @patch("manage._install_deps", return_value=True)
    def test_runs_all_steps(self, deps, db, migrate, css, wizard):
        args = build_parser().parse_args(["setup"])
        cmd_setup(args)

        db.assert_called_once_with("base_app")
        deps.assert_called_once()
        migrate.assert_called_once()
        css.assert_called_once()
        wizard.assert_called_once()

    @patch("manage._install_wizard", return_value=True)
    @patch("manage._build_css", return_value=True)
    @patch("manage._run_migrations", return_value=True)
    @patch("manage._create_databases")
    @patch("manage._install_deps", return_value=False)
    def test_exits_on_deps_failure(self, deps, db, migrate, css, wizard):
        args = build_parser().parse_args(["setup"])
        with pytest.raises(SystemExit) as exc:
            cmd_setup(args)
        assert exc.value.code == 1
        migrate.assert_not_called()

    @patch("manage._install_wizard", return_value=True)
    @patch("manage._build_css", return_value=True)
    @patch("manage._run_migrations", return_value=False)
    @patch("manage._create_databases")
    @patch("manage._install_deps", return_value=True)
    def test_exits_on_migration_failure(self, deps, db, migrate, css, wizard):
        args = build_parser().parse_args(["setup"])
        with pytest.raises(SystemExit) as exc:
            cmd_setup(args)
        assert exc.value.code == 1
        css.assert_not_called()


class TestCmdInit:
    @patch("manage._install_wizard", return_value=True)
    @patch("manage._build_css", return_value=True)
    @patch("manage._run_migrations", return_value=True)
    @patch("manage._install_deps", return_value=True)
    @patch("manage.init_project")
    def test_runs_all_steps(self, mock_ip, deps, migrate, css, wizard):
        mock_ip.validate_name.return_value = None
        mock_ip.rename_project.return_value = {"snake": "my_app", "display": "My App"}

        args = build_parser().parse_args(["init", "my_app"])
        cmd_init(args)

        mock_ip.validate_name.assert_called_once_with("my_app")
        mock_ip.rename_project.assert_called_once_with("my_app")
        mock_ip.reset_docs.assert_called_once()
        mock_ip.create_databases.assert_called_once_with("my_app")
        deps.assert_called_once()
        migrate.assert_called_once()
        css.assert_called_once()
        wizard.assert_called_once()

    @patch("manage._install_wizard", return_value=True)
    @patch("manage._build_css", return_value=True)
    @patch("manage._run_migrations", return_value=True)
    @patch("manage._install_deps", return_value=True)
    @patch("manage.init_project")
    def test_no_db_skips_database_creation(self, mock_ip, deps, migrate, css, wizard):
        mock_ip.validate_name.return_value = None
        mock_ip.rename_project.return_value = {"snake": "my_app", "display": "My App"}

        args = build_parser().parse_args(["init", "my_app", "--no-db"])
        cmd_init(args)

        mock_ip.create_databases.assert_not_called()

    @patch("manage._install_wizard", return_value=True)
    @patch("manage._build_css", return_value=True)
    @patch("manage._run_migrations", return_value=True)
    @patch("manage._install_deps", return_value=False)
    @patch("manage.init_project")
    def test_exits_on_step_failure(self, mock_ip, deps, migrate, css, wizard):
        mock_ip.validate_name.return_value = None
        mock_ip.rename_project.return_value = {"snake": "my_app", "display": "My App"}

        args = build_parser().parse_args(["init", "my_app"])
        with pytest.raises(SystemExit) as exc:
            cmd_init(args)
        assert exc.value.code == 1

    def test_invalid_name_exits(self):
        with pytest.raises(SystemExit) as exc:
            args = build_parser().parse_args(["init", "base_app"])
            cmd_init(args)
        assert exc.value.code == 1

    def test_bad_format_exits(self):
        with pytest.raises(SystemExit) as exc:
            args = build_parser().parse_args(["init", "My-App"])
            cmd_init(args)
        assert exc.value.code == 1
