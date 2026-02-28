"""Template management commands."""
import click
from rich.console import Console
from rich.table import Table
from devtools_cli.core.template_manager import TemplateManager

console = Console()

@click.group()
def template():
    """DevOps template management (CI/CD, Docker, K8s, Terraform)."""
    pass

@template.command(name="list")
@click.option('--category', type=click.Choice(['ci', 'docker', 'k8s', 'terraform']), help='Filter by category')
def list_templates(category: str | None):
    """List available DevOps templates.
    
    Examples:
        devtools template list
        devtools template list --category=docker
    """
    manager = TemplateManager()
    templates = manager.list_templates(category=category)
    
    if not templates:
        console.print("[yellow]No templates found[/yellow]")
        return
    
    table = Table(title="📦 DevOps Templates Registry")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Category", style="magenta")
    table.add_column("Language", style="blue")
    table.add_column("Description")
    
    for t in templates:
        desc = t.description[:60] + "..." if len(t.description) > 60 else t.description
        table.add_row(t.id, t.name, t.category.upper(), t.language, desc)
    
    console.print(table)
    console.print(f"\n[bold]Total:[/bold] {len(templates)} templates")

@template.command(name="init")
@click.argument('template_id')
@click.option('--output', '-o', default='.', help='Output directory')
@click.option('--var', '-v', multiple=True, help='Template variables (key=value)')
def init_template(template_id: str, output: str, var: tuple):
    """Initialize template with variables.
    
    Examples:
        devtools template init github-actions-ci --var PYTHON_VERSION=3.11
        devtools template init python-fastapi -o docker --var APP_NAME=myapi --var PORT=8000
    """
    manager = TemplateManager()
    
    # Parse variables
    variables = {}
    for v in var:
        if '=' not in v:
            console.print(f"[red]Invalid variable format: {v}. Use key=value[/red]")
            raise click.Abort()
        key, value = v.split('=', 1)
        variables[key] = value
    
    # Check template exists
    template_meta = manager.get_template(template_id)
    if not template_meta:
        console.print(f"[red]Template '{template_id}' not found[/red]")
        console.print("\nRun 'devtools template list' to see available templates")
        raise click.Abort()
    
    # Show required variables if missing
    missing_vars = [v for v in template_meta.variables if v not in variables]
    if missing_vars:
        console.print(f"[yellow]Required variables:[/yellow] {', '.join(missing_vars)}")
        console.print("\nExample:")
        example_vars = ' '.join([f'--var {v}=<value>' for v in missing_vars])
        console.print(f"  devtools template init {template_id} {example_vars}")
        raise click.Abort()
    
    # Initialize template
    result = manager.init_template(template_id, output, variables)
    
    if result.success:
        console.print(f"[green]✅ Template '{template_id}' initialized successfully[/green]")
        console.print(f"Output: {result.output_path}")
        for file in result.files_created:
            console.print(f"  Created: {file}")
    else:
        console.print(f"[red]❌ Error: {result.error}[/red]")
        raise click.Abort()

@template.command(name="show")
@click.argument('template_id')
def show_template(template_id: str):
    """Show template details and variables.
    
    Examples:
        devtools template show github-actions-ci
        devtools template show python-fastapi
    """
    manager = TemplateManager()
    template = manager.get_template(template_id)
    
    if not template:
        console.print(f"[red]Template '{template_id}' not found[/red]")
        raise click.Abort()
    
    console.print(f"\n[bold cyan]{template.name}[/bold cyan]")
    console.print(f"[dim]ID: {template.id}[/dim]")
    console.print(f"\n[bold]Category:[/bold] {template.category.upper()}")
    console.print(f"[bold]Language:[/bold] {template.language}")
    console.print(f"\n[bold]Description:[/bold]\n{template.description}")
    
    if template.variables:
        console.print(f"\n[bold]Required Variables:[/bold]")
        for var in template.variables:
            console.print(f"  • {var}")
    
    if template.supports:
        console.print(f"\n[bold]Supports:[/bold]")
        for support in template.supports:
            console.print(f"  • {support}")
    
    console.print(f"\n[bold]File:[/bold] {template.path}")

@template.command(name="categories")
def list_categories():
    """List template categories.
    
    Example:
        devtools template categories
    """
    manager = TemplateManager()
    categories = manager.get_categories()
    
    table = Table(title="📚 Template Categories")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Templates", style="yellow")
    table.add_column("Description")
    
    for cat in categories:
        table.add_row(cat["id"], cat["name"], str(cat["template_count"]), cat["description"])
    
    console.print(table)

@template.command(name="validate")
@click.argument('template_id')
def validate_template(template_id: str):
    """Validate template file exists.
    
    Example:
        devtools template validate github-actions-ci
    """
    manager = TemplateManager()
    is_valid = manager.validate_template(template_id)
    
    if is_valid:
        console.print(f"[green]✅ Template '{template_id}' is valid[/green]")
    else:
        console.print(f"[red]❌ Template '{template_id}' is invalid or not found[/red]")
        raise click.Abort()