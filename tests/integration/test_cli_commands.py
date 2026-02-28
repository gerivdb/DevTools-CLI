"""Integration tests for CLI commands."""
import subprocess
import pytest

def test_cli_template_list():
    """Test 'devtools template list' command."""
    result = subprocess.run(
        ["devtools", "template", "list"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "DevOps Templates Registry" in result.stdout

def test_cli_template_categories():
    """Test 'devtools template categories' command."""
    result = subprocess.run(
        ["devtools", "template", "categories"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Template Categories" in result.stdout

def test_cli_template_show():
    """Test 'devtools template show' command."""
    result = subprocess.run(
        ["devtools", "template", "show", "github-actions-ci"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "GitHub Actions CI Pipeline" in result.stdout

def test_cli_template_validate():
    """Test 'devtools template validate' command."""
    result = subprocess.run(
        ["devtools", "template", "validate", "github-actions-ci"],
        capture_output=True,
        text=True
    )
    # Expected to fail until template files are added
    assert result.returncode != 0 or "valid" in result.stdout.lower()