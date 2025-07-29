"""
Beat Saber Mapping Framework - Utility Functions

This module provides utility functions for common operations like
type conversion, validation, and data manipulation.
"""

import json
from typing import Any, Dict, List, Type, TypeVar, Union
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def ensure_model(data: Union[Dict[str, Any], T], model_class: Type[T]) -> T:
    """
    Ensure that data is an instance of the specified model class

    Args:
        data: Dictionary or model instance
        model_class: Target model class

    Returns:
        Instance of the model class

    Raises:
        TypeError: If data is neither a dict nor an instance of model_class
    """
    if isinstance(data, dict):
        return model_class.model_validate(data)
    elif isinstance(data, model_class):
        return data
    else:
        raise TypeError(
            f"Expected dict or {model_class.__name__}, got {type(data).__name__}"
        )


def ensure_model_list(
    data_list: List[Union[Dict[str, Any], T]], model_class: Type[T]
) -> List[T]:
    """
    Ensure that all items in a list are instances of the specified model class

    Args:
        data_list: List of dictionaries or model instances
        model_class: Target model class

    Returns:
        List of model instances
    """
    return [ensure_model(item, model_class) for item in data_list]


def is_valid_rgba(color: List[float]) -> bool:
    """
    Check if a color value is a valid RGBA color

    Args:
        color: List of RGB or RGBA values

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(color, list):
        return False

    if len(color) not in (3, 4):
        return False

    return all(isinstance(c, (int, float)) and 0 <= c <= 1 for c in color)


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between a minimum and maximum

    Args:
        value: The value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))


def is_valid_json_value(value: Any) -> bool:
    """
    Check if a value can be serialized to JSON

    Args:
        value: Any Python value

    Returns:
        True if the value can be serialized to JSON, False otherwise
    """
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError, ValueError, RecursionError):
        return False
