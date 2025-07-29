"""
Utility functions for HSV module.

This module contains helper functions for working with HSV configurations,
including file operations, conversions, and validation.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Union, List, Dict, Any, Optional, Tuple

from bs_hsv.exceptions import FileError, ValidationError
from bs_hsv.core import HSVConfig, Color


def find_configs(directory: Union[str, Path], recursive: bool = False) -> List[Path]:
    """
    Find HSV configuration files in a directory
    
    Args:
        directory: Directory to search
        recursive: Whether to search subdirectories
        
    Returns:
        List of paths to configuration files
        
    Raises:
        FileError: If the directory doesn't exist
    """
    directory = Path(directory)
    
    if not directory.exists():
        raise FileError(f"Directory does not exist: {directory}")
    
    if not directory.is_dir():
        raise FileError(f"Not a directory: {directory}")
    
    pattern = "**/*.json" if recursive else "*.json"
    config_files = []
    
    for file_path in directory.glob(pattern):
        try:
            # Try to load the file as a JSON to verify it's a valid config
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check if it has judgments key (simple validation)
            if "judgments" in data:
                config_files.append(file_path)
        except:
            # Skip invalid files
            continue
    
    return config_files


def backup_config(config_path: Union[str, Path], 
                 backup_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Create a backup of a configuration file
    
    Args:
        config_path: Path to the configuration file
        backup_dir: Directory for backups (defaults to same directory)
        
    Returns:
        Path to the backup file
        
    Raises:
        FileError: If the backup cannot be created
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileError(f"Configuration file does not exist: {config_path}")
    
    # Determine backup directory
    if backup_dir is None:
        backup_dir = config_path.parent
    else:
        backup_dir = Path(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create backup filename with timestamp
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_name = f"{config_path.stem}_{timestamp}{config_path.suffix}"
    backup_path = backup_dir / backup_name
    
    try:
        shutil.copy2(config_path, backup_path)
        return backup_path
    except Exception as e:
        raise FileError(f"Failed to create backup: {e}") from e


def merge_configs(configs: List[HSVConfig], 
                 strategy: str = "append") -> HSVConfig:
    """
    Merge multiple configurations into one
    
    Args:
        configs: List of HSVConfig objects to merge
        strategy: Merge strategy:
                  - "append": Append all judgments (default)
                  - "unique": Only include unique thresholds
                  - "override": Later configs override earlier ones
    
    Returns:
        A new HSVConfig with merged judgments
        
    Raises:
        ValidationError: If an invalid strategy is provided
    """
    if not configs:
        return HSVConfig()
    
    result = configs[0].clone()
    
    if strategy == "append":
        # Simply append all judgments from all configs
        for config in configs[1:]:
            result.judgments.extend(config.judgments)
        
    elif strategy == "unique":
        # Only include judgments with unique thresholds
        thresholds = {j.threshold for j in result.judgments}
        
        for config in configs[1:]:
            for judgment in config.judgments:
                if judgment.threshold not in thresholds:
                    result.judgments.append(judgment)
                    thresholds.add(judgment.threshold)
    
    elif strategy == "override":
        # Later configs override earlier ones
        judgment_dict = {j.threshold: j for j in result.judgments}
        
        for config in configs[1:]:
            for judgment in config.judgments:
                judgment_dict[judgment.threshold] = judgment
        
        result.judgments = list(judgment_dict.values())
    
    else:
        raise ValidationError(f"Invalid merge strategy: {strategy}")
    
    # Sort judgments
    result.sort_judgments()
    
    # Update metadata
    result.metadata["merged"] = True
    result.metadata["source_count"] = len(configs)
    
    return result


def export_template(output_path: Union[str, Path], 
                   template_type: str = "basic") -> Path:
    """
    Export a template configuration
    
    Args:
        output_path: Path to save the template
        template_type: Type of template:
                       - "basic": Simple template with a few judgments
                       - "detailed": More complex template with many judgments
                       - "minimal": Minimal template with just one judgment
    
    Returns:
        Path to the created template file
        
    Raises:
        ValidationError: If an invalid template type is provided
        FileError: If the template cannot be saved
    """
    config = HSVConfig()
    
    if template_type == "basic":
        config.add(300, "PERFECT", "#FF00FF", fade=True)
        config.add(200, "EXCELLENT", [0, 1, 0, 1])
        config.add(100, "GOOD", Color(r=1, g=0.5, b=0))
        config.add(50, "MISS", "#FF0000")
    
    elif template_type == "detailed":
        config.add(400, "EXTRAORDINARY", "#FFFF00", fade=True)
        config.add(350, "OUTSTANDING", "#FFA500", fade=True)
        config.add(300, "PERFECT", "#FF00FF", fade=True)
        config.add(250, "EXCELLENT", "#00FF00")
        config.add(200, "GREAT", "#00FFFF")
        config.add(150, "GOOD", "#0000FF")
        config.add(100, "DECENT", "#FF0000")
        config.add(50, "MISS", "#800000")
    
    elif template_type == "minimal":
        config.add(100, "HIT", "#FFFFFF")
    
    else:
        raise ValidationError(f"Invalid template type: {template_type}")
    
    config.metadata["template"] = template_type
    
    try:
        output_path = Path(output_path)
        config.save(output_path)
        return output_path
    except Exception as e:
        raise FileError(f"Failed to save template: {e}") from e


def color_interpolate(color1: Color, color2: Color, t: float) -> Color:
    """
    Interpolate between two colors
    
    Args:
        color1: First color
        color2: Second color
        t: Interpolation factor (0-1)
    
    Returns:
        Interpolated color
    """
    t = max(0.0, min(1.0, t))  # Clamp t to 0-1
    
    return Color(
        r=color1.r + t * (color2.r - color1.r),
        g=color1.g + t * (color2.g - color1.g),
        b=color1.b + t * (color2.b - color1.b),
        a=color1.a + t * (color2.a - color1.a)
    )


def generate_color_scheme(base_color: Union[Color, str], 
                         scheme_type: str = "complementary",
                         count: int = 5) -> List[Color]:
    """
    Generate a color scheme based on a base color
    
    Args:
        base_color: Base color (Color object or hex string)
        scheme_type: Type of scheme:
                     - "complementary": Base and complement
                     - "triadic": Three colors equally spaced
                     - "analogous": Adjacent colors
                     - "monochromatic": Same hue, different lightness/saturation
                     - "gradient": Gradient from base color to white/black
        count: Number of colors to generate (for gradient and monochromatic)
    
    Returns:
        List of colors in the scheme
        
    Raises:
        ValidationError: If an invalid scheme type is provided
    """
    # Convert string to Color if needed
    if isinstance(base_color, str):
        base_color = Color.from_hex(base_color)
    
    # Convert to HSV for easier manipulation
    def rgb_to_hsv(color):
        r, g, b = color.r, color.g, color.b
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        delta = max_val - min_val
        
        # Hue calculation
        if delta == 0:
            h = 0
        elif max_val == r:
            h = ((g - b) / delta) % 6
        elif max_val == g:
            h = (b - r) / delta + 2
        else:
            h = (r - g) / delta + 4
        
        h = (h * 60) % 360
        
        # Saturation calculation
        s = 0 if max_val == 0 else delta / max_val
        
        # Value calculation
        v = max_val
        
        return h, s, v
    
    # Convert HSV back to RGB
    def hsv_to_rgb(h, s, v):
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return Color(r=r+m, g=g+m, b=b+m, a=base_color.a)
    
    # Get HSV of base color
    h, s, v = rgb_to_hsv(base_color)
    
    result = []
    
    if scheme_type == "complementary":
        result.append(base_color)
        result.append(hsv_to_rgb((h + 180) % 360, s, v))
    
    elif scheme_type == "triadic":
        result.append(base_color)
        result.append(hsv_to_rgb((h + 120) % 360, s, v))
        result.append(hsv_to_rgb((h + 240) % 360, s, v))
    
    elif scheme_type == "analogous":
        result.append(hsv_to_rgb((h - 30) % 360, s, v))
        result.append(base_color)
        result.append(hsv_to_rgb((h + 30) % 360, s, v))
        
        if count > 3:
            result.append(hsv_to_rgb((h - 60) % 360, s, v))
            result.append(hsv_to_rgb((h + 60) % 360, s, v))
    
    elif scheme_type == "monochromatic":
        # Create variations with different saturations and values
        for i in range(count):
            t = i / (count - 1) if count > 1 else 0
            new_s = max(0, min(1, s - 0.3 + t * 0.6))  # Vary saturation
            new_v = max(0, min(1, v - 0.3 + t * 0.6))  # Vary value
            result.append(hsv_to_rgb(h, new_s, new_v))
    
    elif scheme_type == "gradient":
        # Create a gradient from base color to white or black
        target = Color.white() if v < 0.5 else Color.black()
        for i in range(count):
            t = i / (count - 1) if count > 1 else 0
            result.append(color_interpolate(base_color, target, t))
    
    else:
        raise ValidationError(f"Invalid color scheme type: {scheme_type}")
    
    return result