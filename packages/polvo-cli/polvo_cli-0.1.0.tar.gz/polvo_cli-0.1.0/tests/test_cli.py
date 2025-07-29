import pytest
from typer.testing import CliRunner
from polvo_cli.main import app

runner = CliRunner()


def test_version():
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Polvo CLI v0.1.0" in result.stdout


def test_help():
    """Test help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Polvo CLI" in result.stdout
    assert "Find the best embedding model" in result.stdout


def test_health_command_exists():
    """Test that health command exists."""
    result = runner.invoke(app, ["health", "--help"])
    assert result.exit_code == 0
    assert "Check API health status" in result.stdout


def test_models_command_exists():
    """Test that models command exists."""
    result = runner.invoke(app, ["models", "--help"])
    assert result.exit_code == 0
    assert "List available embedding models" in result.stdout


def test_test_command_exists():
    """Test that test command exists."""
    result = runner.invoke(app, ["test", "--help"])
    assert result.exit_code == 0
    assert "Test embedding models on your dataset" in result.stdout


def test_quick_test_command_exists():
    """Test that quick-test command exists."""
    result = runner.invoke(app, ["quick-test", "--help"])
    assert result.exit_code == 0
    assert "Quick test with a single text" in result.stdout 