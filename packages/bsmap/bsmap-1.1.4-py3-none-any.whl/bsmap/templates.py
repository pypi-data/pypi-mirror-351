"""
Beat Saber Mapping Framework - Template Management

This module provides utilities for saving and loading pattern templates
to speed up mapping workflow.
"""

from typing import Dict, List, Optional, Tuple, Any
import json
import os
from pathlib import Path
import time

from .models import (
    BeatmapFile
)

class TemplateManager:
    """Utility class for managing pattern templates"""
    
    @staticmethod
    def save_template(
        beatmap_section: BeatmapFile,
        name: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        template_dir: str = "./templates"
    ) -> str:
        """
        Save a section of a beatmap as a reusable template
        
        Args:
            beatmap_section: Beatmap section to save as template
            name: Template name
            description: Template description
            tags: List of tags for categorization
            template_dir: Directory to save templates
            
        Returns:
            Path to the saved template file
        """
        # Create template directory if it doesn't exist
        os.makedirs(template_dir, exist_ok=True)
        
        # Sanitize name for filename
        filename = name.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
        
        # Create template metadata
        template = {
            "name": name,
            "description": description,
            "tags": tags or [],
            "created": time.time(),
            "beatmap": beatmap_section.model_dump(exclude_none=True, by_alias=True)
        }
        
        # Save template to file
        file_path = os.path.join(template_dir, f"{filename}.json")
        with open(file_path, "w") as f:
            json.dump(template, f, indent=2)
        
        return file_path
    
    @staticmethod
    def load_template(
        template_name_or_path: str,
        template_dir: str = "./templates"
    ) -> Tuple[BeatmapFile, Dict[str, Any]]:
        """
        Load a template from file
        
        Args:
            template_name_or_path: Template name or full path to template file
            template_dir: Directory where templates are stored
            
        Returns:
            Tuple of (beatmap section, template metadata)
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        # Determine file path
        if os.path.isfile(template_name_or_path):
            file_path = template_name_or_path
        else:
            # Try as a filename
            file_path = os.path.join(template_dir, f"{template_name_or_path}.json")
            if not os.path.isfile(file_path):
                # Try as a template name
                sanitized_name = template_name_or_path.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
                file_path = os.path.join(template_dir, f"{sanitized_name}.json")
        
        # Check if file exists
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Template file not found: {template_name_or_path}")
        
        # Load template from file
        with open(file_path, "r") as f:
            template_data = json.load(f)
        
        # Extract beatmap data
        beatmap_data = template_data.pop("beatmap", {})
        
        # Create beatmap object
        beatmap = BeatmapFile.model_validate(beatmap_data)
        
        return beatmap, template_data
    
    @staticmethod
    def list_templates(template_dir: str = "./templates") -> List[Dict[str, Any]]:
        """
        List all available templates
        
        Args:
            template_dir: Directory where templates are stored
            
        Returns:
            List of template metadata
        """
        templates = []
        
        # Create template directory if it doesn't exist
        os.makedirs(template_dir, exist_ok=True)
        
        # Find all template files
        for file_path in Path(template_dir).glob("*.json"):
            try:
                # Load template metadata
                with open(file_path, "r") as f:
                    template_data = json.load(f)
                
                # Extract metadata (exclude beatmap data to save memory)
                metadata = {
                    "name": template_data.get("name", file_path.stem),
                    "description": template_data.get("description", ""),
                    "tags": template_data.get("tags", []),
                    "created": template_data.get("created", 0),
                    "file_path": str(file_path)
                }
                
                templates.append(metadata)
            except Exception as e:
                print(f"Error loading template {file_path}: {e}")
        
        # Sort by name
        templates.sort(key=lambda t: t["name"])
        
        return templates
    
    @staticmethod
    def search_templates(
        query: str = "",
        tags: Optional[List[str]] = None,
        template_dir: str = "./templates"
    ) -> List[Dict[str, Any]]:
        """
        Search templates by name, description, or tags
        
        Args:
            query: Search term for name or description
            tags: List of tags to filter by
            template_dir: Directory where templates are stored
            
        Returns:
            List of matching template metadata
        """
        # Get all templates
        templates = TemplateManager.list_templates(template_dir)
        
        # Filter by query
        if query:
            query = query.lower()
            templates = [
                t for t in templates 
                if query in t["name"].lower() or query in t["description"].lower()
            ]
        
        # Filter by tags
        if tags:
            templates = [
                t for t in templates 
                if all(tag in t["tags"] for tag in tags)
            ]
        
        return templates