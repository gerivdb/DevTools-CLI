"""Template manager for DevOps templates (CI/CD, Docker, K8s, Terraform)."""
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import jinja2

@dataclass
class TemplateMetadata:
    """Template metadata from registry."""
    id: str
    name: str
    path: str
    language: str
    supports: List[str]
    variables: List[str]
    description: str
    category: str

@dataclass
class TemplateInitResult:
    """Result of template initialization."""
    success: bool
    template_id: str
    output_path: Path
    files_created: List[Path]
    error: Optional[str] = None

class TemplateManager:
    """Manages DevOps templates (CI/CD, Docker, K8s, Terraform)."""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """Initialize Template Manager.
        
        Args:
            templates_dir: Path to templates directory (default: ./templates)
        """
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            # Resolve relative to package root
            self.templates_dir = Path(__file__).parent.parent.parent / "templates"
        
        self.registry_path = self.templates_dir / "registry.json"
        self.registry: Dict[str, Any] = {}
        self.load_registry()
    
    def load_registry(self) -> None:
        """Load template registry from JSON.
        
        Raises:
            FileNotFoundError: If registry.json not found
            json.JSONDecodeError: If registry.json is invalid JSON
        """
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry not found: {self.registry_path}")
        
        with open(self.registry_path) as f:
            self.registry = json.load(f)
    
    def list_templates(self, category: Optional[str] = None) -> List[TemplateMetadata]:
        """List available templates, optionally filtered by category.
        
        Args:
            category: Filter by category (ci, docker, k8s, terraform)
            
        Returns:
            List of TemplateMetadata objects
        """
        templates = []
        
        for cat_id, cat_data in self.registry["categories"].items():
            if category and cat_id != category:
                continue
            
            for template in cat_data["templates"]:
                templates.append(TemplateMetadata(
                    id=template["id"],
                    name=template["name"],
                    path=template["path"],
                    language=template["language"],
                    supports=template["supports"],
                    variables=template["variables"],
                    description=template["description"],
                    category=cat_id
                ))
        
        return templates
    
    def get_template(self, template_id: str) -> Optional[TemplateMetadata]:
        """Get template metadata by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            TemplateMetadata or None if not found
        """
        templates = self.list_templates()
        return next((t for t in templates if t.id == template_id), None)
    
    def init_template(
        self,
        template_id: str,
        output_dir: str,
        variables: Dict[str, str]
    ) -> TemplateInitResult:
        """Initialize template with variable substitution.
        
        Args:
            template_id: Template to initialize
            output_dir: Target directory
            variables: Template variables (key-value pairs)
            
        Returns:
            TemplateInitResult with operation details
        """
        template_meta = self.get_template(template_id)
        if not template_meta:
            return TemplateInitResult(
                success=False,
                template_id=template_id,
                output_path=Path(output_dir),
                files_created=[],
                error=f"Template '{template_id}' not found"
            )
        
        # Load template file
        template_path = self.templates_dir / template_meta.path
        if not template_path.exists():
            return TemplateInitResult(
                success=False,
                template_id=template_id,
                output_path=Path(output_dir),
                files_created=[],
                error=f"Template file not found: {template_path}"
            )
        
        # Validate required variables
        missing_vars = [v for v in template_meta.variables if v not in variables]
        if missing_vars:
            return TemplateInitResult(
                success=False,
                template_id=template_id,
                output_path=Path(output_dir),
                files_created=[],
                error=f"Missing required variables: {', '.join(missing_vars)}"
            )
        
        # Render template with Jinja2
        try:
            with open(template_path) as f:
                template_content = f.read()
            
            jinja_template = jinja2.Template(template_content)
            rendered_content = jinja_template.render(**variables)
            
            # Write output file
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            output_file = output_path / template_path.name
            output_file.write_text(rendered_content)
            
            return TemplateInitResult(
                success=True,
                template_id=template_id,
                output_path=output_path,
                files_created=[output_file]
            )
        
        except Exception as e:
            return TemplateInitResult(
                success=False,
                template_id=template_id,
                output_path=Path(output_dir),
                files_created=[],
                error=str(e)
            )
    
    def validate_template(self, template_id: str) -> bool:
        """Validate template file exists and is parseable.
        
        Args:
            template_id: Template to validate
            
        Returns:
            True if template is valid
        """
        template_meta = self.get_template(template_id)
        if not template_meta:
            return False
        
        template_path = self.templates_dir / template_meta.path
        return template_path.exists()
    
    def get_categories(self) -> List[Dict[str, str]]:
        """Get list of template categories.
        
        Returns:
            List of category metadata dicts
        """
        categories = []
        for cat_id, cat_data in self.registry["categories"].items():
            categories.append({
                "id": cat_id,
                "name": cat_data["name"],
                "description": cat_data["description"],
                "template_count": len(cat_data["templates"])
            })
        return categories