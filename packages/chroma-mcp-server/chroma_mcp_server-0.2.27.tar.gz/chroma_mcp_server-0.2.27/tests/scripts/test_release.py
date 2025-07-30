"""
Unit tests for the release.py script module.
"""

import os
import sys
import re
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

from chroma_mcp.dev_scripts.release import run_command, get_current_version, update_version, update_changelog, main


def test_run_command(tmp_path, monkeypatch):
    """Test the run_command helper."""
    calls = []

    def fake_run(cmd, cwd=None):
        calls.append((cmd, cwd))

        class R:
            returncode = 123

        return R()

    monkeypatch.setattr("subprocess.run", fake_run)
    result = run_command(["echo", "test"], cwd=Path("/tmp"))
    assert result == 123
    assert calls == [(["echo", "test"], Path("/tmp"))]


def test_get_current_version(tmp_path):
    """Test get_current_version reads version from pyproject.toml."""
    content = 'version = "1.2.3"'
    (tmp_path / "pyproject.toml").write_text(content)
    assert get_current_version(tmp_path) == "1.2.3"


def test_update_version(tmp_path):
    """Test update_version replaces the version in pyproject.toml."""
    original = 'name = "pkg"\nversion = "0.1.0"\n'
    project = tmp_path
    file_path = project / "pyproject.toml"
    file_path.write_text(original)
    updated = update_version(project, "0.2.0")
    assert updated is True
    text = file_path.read_text()
    assert re.search(r'version = "0\.2\.0"', text)


def test_update_changelog_creates_and_inserts(tmp_path):
    """Test update_changelog creates CHANGELOG.md if missing and adds entry."""
    project = tmp_path
    version = "2.0.0"
    result = update_changelog(project, version)
    assert result is True
    changelog = project / "CHANGELOG.md"
    assert changelog.exists()
    content = changelog.read_text()
    assert f"## [{version}]" in content


def test_update_changelog_existing(tmp_path):
    """Test update_changelog skips update if version exists."""
    project = tmp_path
    version = "3.0.0"
    text = "# Changelog\n\n## [3.0.0] - 2025-01-01\n"
    (project / "CHANGELOG.md").write_text(text)
    result = update_changelog(project, version)
    assert result is False


@patch("sys.argv", ["release.py", "--dry-run"])
@patch("chroma_mcp.dev_scripts.release.get_current_version")
@patch("chroma_mcp.dev_scripts.release.update_version")
@patch("chroma_mcp.dev_scripts.release.update_changelog")
def test_main_dry_run(mock_update_changelog, mock_update_version, mock_get_current_version):
    """Test main returns immediately on dry-run without making changes."""
    mock_get_current_version.return_value = "1.0.0"
    ret = main()
    assert ret == 0
    mock_update_version.assert_not_called()
    mock_update_changelog.assert_not_called()


@patch("sys.argv", ["release.py"])
@patch("chroma_mcp.dev_scripts.release.get_current_version")
@patch("chroma_mcp.dev_scripts.release.update_version")
@patch("chroma_mcp.dev_scripts.release.update_changelog")
@patch("chroma_mcp.dev_scripts.release.run_command")
def test_main_guided_default(mock_run_command, mock_update_changelog, mock_update_version, mock_get_current_version):
    """Test guided release default flow without skip flags."""
    mock_get_current_version.return_value = "1.0.0"
    mock_update_version.return_value = True
    mock_update_changelog.return_value = True
    mock_run_command.return_value = 0
    ret = main()
    assert ret == 0
    calls = [args[0] for (args, _) in mock_run_command.call_args_list]
    assert len(calls) == 2
    # First call is TestPyPI
    assert calls[0][:3] == ["hatch", "run", "publish-mcp"]
    assert "--repo" in calls[0] and "testpypi" in calls[0]
    # Second call is Production
    assert calls[1][:3] == ["hatch", "run", "publish-mcp"]
    assert "--repo" in calls[1] and "pypi" in calls[1]


@patch("sys.argv", ["release.py", "--skip-testpypi"])
@patch("chroma_mcp.dev_scripts.release.get_current_version")
@patch("chroma_mcp.dev_scripts.release.update_version")
@patch("chroma_mcp.dev_scripts.release.update_changelog")
@patch("chroma_mcp.dev_scripts.release.run_command")
def test_main_guided_skip_testpypi(
    mock_run_command, mock_update_changelog, mock_update_version, mock_get_current_version
):
    """Test guided release with --skip-testpypi."""
    mock_get_current_version.return_value = "1.0.0"
    mock_update_version.return_value = True
    mock_update_changelog.return_value = True
    mock_run_command.return_value = 0
    ret = main()
    assert ret == 0
    calls = [args[0] for (args, _) in mock_run_command.call_args_list]
    assert len(calls) == 1
    # Only Production call
    assert calls[0][:3] == ["hatch", "run", "publish-mcp"]
    assert "--repo" in calls[0] and "pypi" in calls[0]


@patch("sys.argv", ["release.py", "--test-only"])
@patch("chroma_mcp.dev_scripts.release.get_current_version")
@patch("chroma_mcp.dev_scripts.release.update_version")
@patch("chroma_mcp.dev_scripts.release.update_changelog")
@patch("chroma_mcp.dev_scripts.release.run_command")
def test_main_guided_test_only(mock_run_command, mock_update_changelog, mock_update_version, mock_get_current_version):
    """Test guided release with --test-only."""
    mock_get_current_version.return_value = "1.0.0"
    mock_update_version.return_value = True
    mock_update_changelog.return_value = True
    mock_run_command.return_value = 0
    ret = main()
    assert ret == 0
    calls = [args[0] for (args, _) in mock_run_command.call_args_list]
    assert len(calls) == 1
    # Only TestPyPI call
    assert calls[0][:3] == ["hatch", "run", "publish-mcp"]
    assert "--repo" in calls[0] and "testpypi" in calls[0]


@patch("sys.argv", ["release.py", "--skip-tests", "--skip-build"])
@patch("chroma_mcp.dev_scripts.release.get_current_version")
@patch("chroma_mcp.dev_scripts.release.update_version")
@patch("chroma_mcp.dev_scripts.release.update_changelog")
@patch("chroma_mcp.dev_scripts.release.run_command")
def test_main_guided_skip_tests_build(
    mock_run_command, mock_update_changelog, mock_update_version, mock_get_current_version
):
    """Test guided release with --skip-tests and --skip-build flags."""
    mock_get_current_version.return_value = "1.0.0"
    mock_update_version.return_value = True
    mock_update_changelog.return_value = True
    mock_run_command.return_value = 0
    ret = main()
    assert ret == 0
    calls = [args[0] for (args, _) in mock_run_command.call_args_list]
    assert len(calls) == 2
    # Both calls should include skip flags
    for call in calls:
        assert "--skip-tests" in call and "--skip-build" in call
