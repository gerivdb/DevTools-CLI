"""Unit tests for TemplateManager."""
import pytest
import json
from pathlib import Path
from devtools_cli.core.template_manager import TemplateManager, TemplateMetadata

def test_load_registry():
    """Test registry loading."""
    manager = TemplateManager()
    assert "categories" in manager.registry
    assert "version" in manager.registry

def test_list_templates():
    """Test listing all templates."""
    manager = TemplateManager()
    templates = manager.list_templates()
    assert len(templates) > 0
    assert all(isinstance(t, TemplateMetadata) for t in templates)

def test_list_templates_by_category():
    """Test filtering templates by category."""
    manager = TemplateManager()
    ci_templates = manager.list_templates(category="ci")
    assert len(ci_templates) > 0
    assert all(t.category == "ci" for t in ci_templates)

def test_get_template():
    """Test getting single template by ID."""
    manager = TemplateManager()
    template = manager.get_template("github-actions-ci")
    assert template is not None
    assert template.id == "github-actions-ci"

def test_get_template_not_found():
    """Test getting non-existent template."""
    manager = TemplateManager()
    template = manager.get_template("unknown-template")
    assert template is None

def test_get_categories():
    """Test getting category list."""
    manager = TemplateManager()
    categories = manager.get_categories()
    assert len(categories) == 4
    assert any(c["id"] == "ci" for c in categories)
    assert any(c["id"] == "docker" for c in categories)