"""
Beat Saber Mapping Framework

A comprehensive framework for creating, editing, and validating Beat Saber maps
using Pydantic models for type safety and validation.

Common Errors:
- AttributeError: 'dict' object has no attribute 'x' - This occurs when a dictionary is used 
    instead of a proper model object. Make sure to use the appropriate model classes 
    (ColorNote, RotationEvent, etc.) instead of raw dictionaries.

- TypeError: Object of type x is not JSON serializable - This can happen if you've added custom 
    Python objects to customData. Make sure all data is JSON serializable.

- ValueError: field required - This occurs when a required field is missing when creating a model.
    Check the model definition to see which fields are required.
"""

# Version info
__version__ = "1.0.0"
__author__ = "CodeSoftGit"

# Core models
from .models import (
        InfoDat, BeatmapFile, ColorNote, BombNote, Obstacle, Slider, BurstSlider, 
        BasicBeatmapEvent, ColorBoostBeatmapEvent, CustomEvent, Difficulty, Characteristic,
        NoteColor, NoteDirection, RotationEvent, BPMEvent, Waypoint
)

# Custom data models
from .custom_data import (
        Settings, PlayerOptions, Modifiers, Environments, Colors, Graphics, Chroma,
        NoodleExtensions, ChromaData, Animation
)

# Main utilities
from .mapper import BeatSaberMapper
from .analysis import MapAnalysis
from .operations import MapOperations
from .autolights import LightingAutomation
from .templates import TemplateManager

# Helper functions
from .utils import ensure_model, ensure_model_list, is_valid_rgba, clamp, is_valid_json_value

# Organize exports by category
__all__ = [
        # Version info
        "__version__",
        "__author__",
        
        # Enums
        "Difficulty", 
        "Characteristic", 
        "NoteColor", 
        "NoteDirection",
        
        # Core models
        "InfoDat", 
        "BeatmapFile", 
        "ColorNote", 
        "BombNote", 
        "Obstacle", 
        "Slider", 
        "BurstSlider", 
        "BasicBeatmapEvent", 
        "ColorBoostBeatmapEvent", 
        "CustomEvent",
        "RotationEvent", 
        "BPMEvent", 
        "Waypoint",
        
        # Custom data models
        "Settings", 
        "PlayerOptions", 
        "Modifiers", 
        "Environments", 
        "Colors",
        "Graphics", 
        "Chroma", 
        "NoodleExtensions", 
        "ChromaData", 
        "Animation",
        
        # Main utilities
        "BeatSaberMapper",
        "MapAnalysis",
        "MapOperations",
        "LightingAutomation",
        "TemplateManager",
        
        # Helper functions
        "ensure_model", 
        "ensure_model_list", 
        "is_valid_rgba", 
        "clamp", 
        "is_valid_json_value"
]