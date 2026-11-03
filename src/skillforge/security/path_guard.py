"""Security Path Guard for Safe File Access and Traversal Prevention."""

import os
from pathlib import Path


class PathTraversalError(PermissionError):
    pass


def validate_safe_relative_path(base_dir: str | Path, relative_path: str) -> Path:
    """Validate that relative_path resolves strictly within base_dir.
    
    Prevents directory traversal (e.g., ../../Windows/System32 or ..\\..\\secrets).
    """
    base = Path(base_dir).resolve()
    
    # Strip leading slashes to prevent root-relative lookups
    clean_rel = relative_path.lstrip("/\\")
    
    target = (base / clean_rel).resolve()
    
    # Ensure target path starts with base directory path
    try:
        target.relative_to(base)
    except ValueError:
        raise PathTraversalError(f"Path traversal attempt detected: {relative_path} outside {base}")
        
    return target


def is_safe_resource_path(base_dir: str | Path, relative_path: str) -> bool:
    """Boolean check for whether relative_path is within base_dir."""
    try:
        validate_safe_relative_path(base_dir, relative_path)
        return True
    except (PathTraversalError, ValueError):
        return False


class PathGuard:
    """Security guard class to validate safe file access and prevent path traversal."""

    @staticmethod
    def validate_safe_path(base_dir: str | Path, relative_path: str) -> Path:
        return validate_safe_relative_path(base_dir, relative_path)

    @staticmethod
    def is_safe(base_dir: str | Path, relative_path: str) -> bool:
        return is_safe_resource_path(base_dir, relative_path)
