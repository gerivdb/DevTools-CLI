"""DevTools CLI entry point."""
import click
from devtools_cli.commands.template import template

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """DevTools CLI - DevOps Templates \u0026 Quality Automation for Ecosystem-1.
    
    Examples:
        devtools template list
        devtools template init github-actions-ci --var PYTHON_VERSION=3.11
        devtools template show python-fastapi
    """
    pass

# Register command groups
cli.add_command(template)

if __name__ == "__main__":
    cli()