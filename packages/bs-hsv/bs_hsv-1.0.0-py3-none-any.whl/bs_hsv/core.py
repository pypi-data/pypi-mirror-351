"""
Core data models for HSV module.

This module contains the primary data structures used throughout the HSV package,
including Color, Judgment, and HSVConfig classes.
"""

import json
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, Callable, TypeVar, cast
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

from bs_hsv.exceptions import ValidationError, FileError


class Color(BaseModel):
    """
    Represents an RGBA color with values between 0.0 and 1.0.
    
    Attributes:
        r (float): Red component (0-1)
        g (float): Green component (0-1)
        b (float): Blue component (0-1)
        a (float): Alpha component (0-1)
    """
    model_config = ConfigDict(frozen=True)  # Make immutable for safety
    
    r: float = Field(default=1.0, ge=0.0, le=1.0, description="Red component (0-1)")
    g: float = Field(default=1.0, ge=0.0, le=1.0, description="Green component (0-1)")
    b: float = Field(default=1.0, ge=0.0, le=1.0, description="Blue component (0-1)")
    a: float = Field(default=1.0, ge=0.0, le=1.0, description="Alpha component (0-1)")

    @classmethod
    def white(cls) -> "Color":
        """Returns white color (1,1,1,1)"""
        return cls(r=1.0, g=1.0, b=1.0, a=1.0)
    
    @classmethod
    def black(cls) -> "Color":
        """Returns black color (0,0,0,1)"""
        return cls(r=0.0, g=0.0, b=0.0, a=1.0)
    
    @classmethod
    def transparent(cls) -> "Color":
        """Returns transparent color (0,0,0,0)"""
        return cls(r=0.0, g=0.0, b=0.0, a=0.0)
    
    @classmethod
    def red(cls) -> "Color":
        """Returns red color (1,0,0,1)"""
        return cls(r=1.0, g=0.0, b=0.0)
    
    @classmethod
    def green(cls) -> "Color":
        """Returns green color (0,1,0,1)"""
        return cls(r=0.0, g=1.0, b=0.0)
    
    @classmethod
    def blue(cls) -> "Color":
        """Returns blue color (0,0,1,1)"""
        return cls(r=0.0, g=0.0, b=1.0)
    
    @classmethod
    def yellow(cls) -> "Color":
        """Returns yellow color (1,1,0,1)"""
        return cls(r=1.0, g=1.0, b=0.0)
    
    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> "Color":
        """
        Create a Color from RGB values (0-255)
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            
        Returns:
            A new Color instance
        """
        return cls(r=r/255, g=g/255, b=b/255)
    
    @classmethod
    def from_rgba(cls, r: int, g: int, b: int, a: int) -> "Color":
        """
        Create a Color from RGBA values (0-255)
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            a: Alpha component (0-255)
            
        Returns:
            A new Color instance
        """
        return cls(r=r/255, g=g/255, b=b/255, a=a/255)
    
    @classmethod
    def from_hex(cls, hex_code: str) -> "Color":
        """
        Create a Color from a hex string (e.g. '#FF00FF' or 'FF00FF')
        
        Args:
            hex_code: A color in hexadecimal format
            
        Returns:
            A new Color instance
            
        Raises:
            ValueError: If the hex code is invalid
        """
        if hex_code.startswith('#'):
            hex_code = hex_code[1:]
        
        try:
            if len(hex_code) == 3:  # Shorthand hex like #F00
                r = int(hex_code[0] + hex_code[0], 16) / 255
                g = int(hex_code[1] + hex_code[1], 16) / 255
                b = int(hex_code[2] + hex_code[2], 16) / 255
                return cls(r=r, g=g, b=b)
            elif len(hex_code) == 6:  # Standard hex like #FF0000
                r = int(hex_code[0:2], 16) / 255
                g = int(hex_code[2:4], 16) / 255
                b = int(hex_code[4:6], 16) / 255
                return cls(r=r, g=g, b=b)
            elif len(hex_code) == 8:  # Hex with alpha like #FF0000FF
                r = int(hex_code[0:2], 16) / 255
                g = int(hex_code[2:4], 16) / 255
                b = int(hex_code[4:6], 16) / 255
                a = int(hex_code[6:8], 16) / 255
                return cls(r=r, g=g, b=b, a=a)
            else:
                raise ValueError(f"Invalid hex color length: {len(hex_code)}")
        except ValueError as e:
            raise ValidationError(f"Invalid hex color format: {hex_code}") from e
    
    def to_hex(self, include_alpha: bool = False) -> str:
        """
        Convert to hex string
        
        Args:
            include_alpha: Whether to include alpha in the hex string
            
        Returns:
            Hex color string in format #RRGGBB or #RRGGBBAA
        """
        r = int(self.r * 255)
        g = int(self.g * 255)
        b = int(self.b * 255)
        
        if include_alpha:
            a = int(self.a * 255)
            return f"#{r:02X}{g:02X}{b:02X}{a:02X}"
        return f"#{r:02X}{g:02X}{b:02X}"
    
    def to_rgba(self) -> List[float]:
        """
        Convert to RGBA list [r, g, b, a]
        
        Returns:
            A list of the color components [r, g, b, a]
        """
        return [self.r, self.g, self.b, self.a]
    
    def to_rgb_tuple(self) -> tuple:
        """
        Convert to RGB tuple with values 0-255
        
        Returns:
            Tuple (r, g, b) with values from 0-255
        """
        return (int(self.r * 255), int(self.g * 255), int(self.b * 255))
    
    def with_alpha(self, alpha: float) -> "Color":
        """
        Create a new color with modified alpha
        
        Args:
            alpha: New alpha value (0-1)
            
        Returns:
            A new Color instance with the specified alpha
        """
        return Color(r=self.r, g=self.g, b=self.b, a=alpha)
    
    def lighten(self, amount: float = 0.1) -> "Color":
        """
        Create a lightened version of this color
        
        Args:
            amount: Amount to lighten by (0-1)
            
        Returns:
            A new Color instance
        """
        return Color(
            r=min(1.0, self.r + amount),
            g=min(1.0, self.g + amount),
            b=min(1.0, self.b + amount),
            a=self.a
        )
    
    def darken(self, amount: float = 0.1) -> "Color":
        """
        Create a darkened version of this color
        
        Args:
            amount: Amount to darken by (0-1)
            
        Returns:
            A new Color instance
        """
        return Color(
            r=max(0.0, self.r - amount),
            g=max(0.0, self.g - amount),
            b=max(0.0, self.b - amount),
            a=self.a
        )
    
    def __str__(self) -> str:
        return self.to_hex()


class Judgment(BaseModel):
    """
    Represents a hit score judgment with threshold, text, and styling
    
    Attributes:
        threshold (float): Score threshold for this judgment
        text (str): Text to display
        color (Color): Color for the text
        fade (bool): Whether the text should fade
    """
    threshold: float = Field(..., description="Score threshold for this judgment")
    text: str = Field(..., description="Text to display")
    color: Color = Field(default_factory=Color.white, description="Color for the text")
    fade: bool = Field(default=False, description="Whether the text should fade")
    
    def __lt__(self, other: "Judgment") -> bool:
        """Compare judgments by threshold for sorting"""
        if not isinstance(other, Judgment):
            return NotImplemented
        return self.threshold < other.threshold
    
    def __eq__(self, other: object) -> bool:
        """Compare judgments for equality"""
        if not isinstance(other, Judgment):
            return NotImplemented
        return (self.threshold == other.threshold and
                self.text == other.text and
                self.color == other.color and
                self.fade == other.fade)


T = TypeVar('T', bound='HSVConfig')

class HSVConfig(BaseModel):
    """
    Hit Score Visualization configuration
    
    This class manages a collection of Judgment objects that define
    how scores should be displayed based on thresholds.
    
    Attributes:
        judgments (List[Judgment]): List of judgment definitions
        metadata (Dict): Optional metadata for the configuration
    """
    judgments: List[Judgment] = Field(default_factory=list, description="List of judgments")
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "created": datetime.now().isoformat(),
            "version": "1.0.0"
        },
        description="Metadata for the configuration"
    )
    
    @model_validator(mode="after")
    def sort_judgments(self) -> "HSVConfig":
        """Ensure judgments are sorted by threshold (highest first)"""
        self.judgments.sort(reverse=True)
        return self
    
    def add(self, threshold: float, text: str, 
           color: Union[Color, List[float], str] = None, 
           fade: bool = False) -> "HSVConfig":
        """
        Add a new judgment to the configuration.
        
        Args:
            threshold: The threshold score for this judgment
            text: The text to display
            color: Color for the text (Color object, RGBA list [r,g,b,a], or hex string)
            fade: Whether the text should fade
            
        Returns:
            Self for method chaining
            
        Raises:
            ValidationError: If the color format is invalid
        """
        # Handle different color input types
        if color is None:
            color = Color.white()
        elif isinstance(color, list):
            if len(color) == 3:
                color = Color(r=color[0], g=color[1], b=color[2])
            elif len(color) == 4:
                color = Color(r=color[0], g=color[1], b=color[2], a=color[3])
            else:
                raise ValidationError(f"Invalid color list: {color}. Must be [r,g,b] or [r,g,b,a]")
        elif isinstance(color, str):
            try:
                color = Color.from_hex(color)
            except ValidationError as e:
                raise ValidationError(f"Invalid color string: {color}") from e
        elif not isinstance(color, Color):
            raise ValidationError(f"Invalid color type: {type(color)}. Must be Color, list, or str")
        
        self.judgments.append(Judgment(
            threshold=threshold,
            text=text,
            color=color,
            fade=fade
        ))
        
        # Sort judgments by threshold (highest first)
        self.sort_judgments()
        return self
    
    def add_image(self, threshold: float, image_path: Union[str, Path], 
                 color: Union[Color, List[float], str] = None,
                 fade: bool = False, max_width: int = 50) -> "HSVConfig":
        """
        Add a judgment with text art generated from an image.
        
        Args:
            threshold: The threshold score for this judgment
            image_path: Path to the image file
            color: Optional base color for the text art
            fade: Whether the text should fade
            max_width: Maximum width for the generated text art
            
        Returns:
            Self for method chaining
            
        Raises:
            FileError: If the image file cannot be accessed
            ValidationError: If the color format is invalid
        """
        from hsv.generators import TextArtGenerator
        
        try:
            text_art = TextArtGenerator.from_image(image_path, max_width=max_width)
            return self.add(threshold, text_art, color, fade)
        except Exception as e:
            raise FileError(f"Failed to process image: {image_path}") from e
    
    def remove(self, threshold: float) -> "HSVConfig":
        """
        Remove a judgment by threshold
        
        Args:
            threshold: The threshold of the judgment to remove
            
        Returns:
            Self for method chaining
        """
        self.judgments = [j for j in self.judgments if j.threshold != threshold]
        return self
    
    def get_judgment_for_score(self, score: float) -> Optional[Judgment]:
        """
        Get the appropriate judgment for a given score
        
        Args:
            score: The score to find a judgment for
            
        Returns:
            The matching Judgment or None if no judgment applies
        """
        for judgment in self.judgments:
            if score >= judgment.threshold:
                return judgment
        return None
    
    def save(self, file_path: Union[str, Path]) -> None:
        """
        Save configuration to a JSON file
        
        Args:
            file_path: Path to save the JSON file
            
        Raises:
            FileError: If the file cannot be written
        """
        file_path = Path(file_path)
        
        # Update metadata
        self.metadata["updated"] = datetime.now().isoformat()
        
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(self.model_dump_json(indent=4))
        except Exception as e:
            raise FileError(f"Failed to save config to {file_path}") from e
    
    @classmethod
    def load(cls: type[T], file_path: Union[str, Path]) -> T:
        """
        Load configuration from a JSON file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            An HSVConfig instance
            
        Raises:
            FileError: If the file cannot be read or parsed
        """
        file_path = Path(file_path)
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Update metadata to show when loaded
            if "metadata" in data:
                data["metadata"]["loaded"] = datetime.now().isoformat()
            
            return cls.model_validate(data)
        except json.JSONDecodeError as e:
            raise FileError(f"Invalid JSON in {file_path}") from e
        except Exception as e:
            raise FileError(f"Failed to load config from {file_path}") from e
    
    def clone(self: T) -> T:
        """
        Create a deep copy of this configuration
        
        Returns:
            A new HSVConfig instance with the same judgments
        """
        return self.__class__.model_validate(self.model_dump())
    
    def __len__(self) -> int:
        """Return the number of judgments"""
        return len(self.judgments)
    
    def __repr__(self) -> str:
        judgments_str = "\n  ".join(
            f"{j.threshold}: '{j.text[:20]}{'...' if len(j.text) > 20 else ''}' "
            f"(color={j.color.to_hex()}, fade={j.fade})" 
            for j in self.judgments
        )
        return f"HSVConfig with {len(self.judgments)} judgments:\n  {judgments_str}"