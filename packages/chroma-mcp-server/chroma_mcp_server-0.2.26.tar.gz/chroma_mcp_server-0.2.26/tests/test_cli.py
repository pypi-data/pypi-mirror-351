"""Tests for the CLI argument parsing."""

import pytest
import argparse
import os
from unittest.mock import patch, MagicMock
import logging
import sys
from typing import List, Optional

# Import the function to test
from src.chroma_mcp.cli import parse_args, main as cli_main

# Assume cli.py is in the parent directory structure or PYTHONPATH is set
from src.chroma_mcp import cli

# Define a dictionary of default expected values (based on cli.py defaults and getenv fallbacks)
# Note: data_dir, log_dir, host, port, tenant, database, api_key default to None if env var not set
DEFAULT_EXPECTED = {
    "mode": "http",
    "client_type": "ephemeral",
    "embedding_function_name": "default",
    "data_dir": None,
    "log_dir": None,
    "host": None,
    "port": None,
    "ssl": True,  # Default from getenv is 'true'
    "tenant": None,
    "database": None,
    "api_key": None,
    "dotenv_path": ".env",
    "cpu_execution_provider": "auto",
}


def test_parse_args_defaults():
    """Test parsing with default values (no args, no env vars)."""
    # Ensure environment variables are clear for this test
    with patch.dict(os.environ, {}, clear=True):
        args = parse_args([])
        assert args.mode == "http", "Default mode should be http"
        for key, value in DEFAULT_EXPECTED.items():
            assert getattr(args, key) == value, f"Default failed for {key}"


def test_parse_args_cmd_line_overrides():
    """Test parsing with command line arguments overriding defaults."""
    cmd_args = [
        "--mode",
        "stdio",
        "--client-type",
        "persistent",
        "--data-dir",
        "/tmp/chroma_data",
        "--log-dir",
        "/var/log/chroma",
        "--host",
        "localhost",
        "--port",
        "9000",
        "--ssl",
        "false",  # Test boolean parsing
        "--tenant",
        "my-tenant",
        "--database",
        "my-db",
        "--api-key",
        "ABCDEF",
        "--dotenv-path",
        "/etc/chroma/.env",
        "--cpu-execution-provider",
        "true",
        "--embedding-function",
        "openai",
    ]
    # Ensure environment variables are clear
    with patch.dict(os.environ, {}, clear=True):
        args = parse_args(cmd_args)
        assert args.mode == "stdio"
        assert args.client_type == "persistent"
        assert args.data_dir == "/tmp/chroma_data"
        assert args.log_dir == "/var/log/chroma"
        assert args.host == "localhost"
        assert args.port == "9000"
        assert args.ssl is False  # Check boolean conversion
        assert args.tenant == "my-tenant"
        assert args.database == "my-db"
        assert args.api_key == "ABCDEF"
        assert args.dotenv_path == "/etc/chroma/.env"
        assert args.cpu_execution_provider == "true"
        assert args.embedding_function_name == "openai"


def test_parse_args_env_vars():
    """Test parsing with environment variables providing values."""
    env_vars = {
        "CHROMA_SERVER_MODE": "stdio",
        "CHROMA_CLIENT_TYPE": "http",
        "CHROMA_DATA_DIR": "/data",
        "CHROMA_LOG_DIR": "/logs",
        "CHROMA_HOST": "192.168.1.100",
        "CHROMA_PORT": "8888",
        "CHROMA_SSL": "false",
        "CHROMA_TENANT": "env-tenant",
        "CHROMA_DATABASE": "env-db",
        "CHROMA_API_KEY": "XYZ123",
        "CHROMA_DOTENV_PATH": ".env.prod",
        "CHROMA_CPU_EXECUTION_PROVIDER": "false",
        "CHROMA_EMBEDDING_FUNCTION": "accurate",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        args = parse_args([])  # No command line args
        assert args.mode == "stdio"
        assert args.client_type == "http"
        assert args.data_dir == "/data"
        assert args.log_dir == "/logs"
        assert args.host == "192.168.1.100"
        assert args.port == "8888"
        assert args.ssl is False
        assert args.tenant == "env-tenant"
        assert args.database == "env-db"
        assert args.api_key == "XYZ123"
        assert args.dotenv_path == ".env.prod"
        assert args.cpu_execution_provider == "false"
        assert args.embedding_function_name == "accurate"


def test_parse_args_cmd_line_overrides_env():
    """Test command line args overriding environment variables."""
    env_vars = {
        "CHROMA_SERVER_MODE": "http",
        "CHROMA_CLIENT_TYPE": "http",
        "CHROMA_PORT": "8000",
        "CHROMA_SSL": "true",
        "CHROMA_EMBEDDING_FUNCTION": "default",
    }
    cmd_args = [
        "--mode",
        "stdio",
        "--client-type",
        "persistent",  # Override env
        "--port",
        "9999",  # Override env
        "--ssl",
        "false",  # Override env
        "--embedding-function",
        "gemini",
    ]
    with patch.dict(os.environ, env_vars, clear=True):
        args = parse_args(cmd_args)
        assert args.mode == "stdio"
        assert args.client_type == "persistent"  # Prefers cmd line
        assert args.port == "9999"  # Prefers cmd line
        assert args.ssl is False  # Prefers cmd line
        # Check that unset values still use defaults (or None if no default env)
        assert args.host is None
        assert args.data_dir is None
        assert args.embedding_function_name == "gemini"


def test_parse_args_ssl_variations():
    """Test various inputs for the boolean --ssl flag."""
    with patch.dict(os.environ, {}, clear=True):
        # True variations
        assert parse_args(["--ssl", "true"]).ssl is True
        assert parse_args(["--ssl", "YES"]).ssl is True
        assert parse_args(["--ssl", "1"]).ssl is True
        assert parse_args(["--ssl", "T"]).ssl is True
        assert parse_args(["--ssl", "y"]).ssl is True

        # False variations
        assert parse_args(["--ssl", "false"]).ssl is False
        assert parse_args(["--ssl", "NO"]).ssl is False
        assert parse_args(["--ssl", "0"]).ssl is False
        assert parse_args(["--ssl", "F"]).ssl is False
        assert parse_args(["--ssl", "n"]).ssl is False
        assert parse_args(["--ssl", "any_other_string"]).ssl is False  # Default argparse bool behavior

        # Default (should be True based on cli.py getenv default)
        assert parse_args([]).ssl is True


# --- Tests for cli.main() Error Handling ---


@patch("src.chroma_mcp.cli.parse_args")
@patch("src.chroma_mcp.cli._initialize_chroma_client")
@patch("asyncio.run")  # Patch asyncio.run used in stdio path
def test_cli_main_stdio_keyboard_interrupt(mock_asyncio_run, mock_init_client, mock_parse_args):
    """Test cli.main() handles KeyboardInterrupt gracefully in stdio mode."""
    # Simulate parse_args returning args for stdio mode
    mock_args = MagicMock()
    mock_args.mode = "stdio"
    mock_parse_args.return_value = mock_args

    # Simulate KeyboardInterrupt during asyncio.run
    mock_asyncio_run.side_effect = KeyboardInterrupt

    # Call main and check return code
    result = cli_main()  # Use the imported cli_main
    assert result == 0  # Clean exit on Ctrl+C
    mock_init_client.assert_called_once_with(mock_args)  # Check client init was called
    mock_asyncio_run.assert_called_once()  # Ensure stdio path was attempted


@patch("src.chroma_mcp.cli.parse_args")
@patch("src.chroma_mcp.cli._initialize_chroma_client")
@patch("asyncio.run")  # Patch asyncio.run used in stdio path
def test_cli_main_stdio_generic_exception(mock_asyncio_run, mock_init_client, mock_parse_args):
    """Test cli.main() handles generic Exceptions gracefully in stdio mode."""
    # Simulate parse_args returning args for stdio mode
    mock_args = MagicMock()
    mock_args.mode = "stdio"
    mock_parse_args.return_value = mock_args

    # Simulate a generic exception during asyncio.run
    test_exception = ValueError("Test Error")
    mock_asyncio_run.side_effect = test_exception

    # Call main and check return code
    result = cli_main()
    assert result == 1  # Error exit code
    mock_init_client.assert_called_once_with(mock_args)  # Check client init was called
    mock_asyncio_run.assert_called_once()  # Ensure stdio path was attempted


@patch("src.chroma_mcp.cli.parse_args")
@patch("src.chroma_mcp.cli.config_server")  # Patch config_server called in http path
@patch("src.chroma_mcp.cli.server_main")  # Patch server_main called in http path
def test_cli_main_http_keyboard_interrupt(mock_server_main, mock_config_server, mock_parse_args):
    """Test cli.main() handles KeyboardInterrupt gracefully in http mode."""
    mock_args = MagicMock()
    mock_args.mode = "http"
    mock_parse_args.return_value = mock_args

    # Simulate KeyboardInterrupt during server_main
    mock_server_main.side_effect = KeyboardInterrupt

    result = cli_main()
    assert result == 0
    mock_config_server.assert_called_once_with(mock_args)
    mock_server_main.assert_called_once()


@patch("src.chroma_mcp.cli.parse_args")
@patch("src.chroma_mcp.cli.config_server")  # Patch config_server called in http path
@patch("src.chroma_mcp.cli.server_main")  # Patch server_main called in http path
def test_cli_main_http_generic_exception(mock_server_main, mock_config_server, mock_parse_args):
    """Test cli.main() handles generic Exceptions gracefully in http mode."""
    mock_args = MagicMock()
    mock_args.mode = "http"
    mock_parse_args.return_value = mock_args

    # Simulate a generic exception during server_main
    test_exception = ValueError("HTTP Test Error")
    mock_server_main.side_effect = test_exception

    result = cli_main()
    assert result == 1
    mock_config_server.assert_called_once_with(mock_args)
    mock_server_main.assert_called_once()


@patch("src.chroma_mcp.cli.parse_args")
@patch("src.chroma_mcp.cli.config_server")  # Patch config_server called in http path
@patch("src.chroma_mcp.cli.server_main")  # Patch server_main called in http path
def test_cli_main_http_success(mock_server_main, mock_config_server, mock_parse_args):
    """Test cli.main() successful execution in http mode."""
    mock_args = MagicMock()
    mock_args.mode = "http"
    mock_parse_args.return_value = mock_args

    # Simulate server_main running without error
    mock_server_main.return_value = None

    result = cli_main()
    assert result == 0  # Expect 0 on normal HTTP exit now
    mock_config_server.assert_called_once_with(mock_args)
    mock_server_main.assert_called_once()


# --- main Tests ---
