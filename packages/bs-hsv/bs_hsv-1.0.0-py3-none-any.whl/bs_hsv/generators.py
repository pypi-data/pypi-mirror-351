"""
Text and visual generators for HSV module.

This module contains utilities for generating text art and other
visual representations for hit score judgments.
"""

from pathlib import Path
from typing import Union

from PIL import Image

from bs_hsv.exceptions import FileError


class TextArtGenerator:
    """Utility class for generating text art from images and other sources"""
    
    @staticmethod
    def from_image(image_path: Union[str, Path], max_width: int = 50, 
                  pixel_char: str = '█') -> str:
        """
        Converts an image into colored ASCII art using TextMeshPro tags.
        
        Args:
            image_path: Path to the image file
            max_width: Maximum width for the generated text art
            pixel_char: Character to use for each pixel
            
        Returns:
            A string containing colored ASCII art with TextMeshPro tags
            
        Raises:
            FileError: If the image file cannot be accessed or processed
        """
        try:
            # Load the image
            img = Image.open(image_path)
            
            # Get image dimensions
            width, height = img.size
            
            # Calculate size tag scaling based on image width
            base_size = 20
            size_tag = f"<size={base_size}%>"
            
            # Adjust the width for a better aspect ratio
            if width > max_width:
                aspect_ratio = height / width
                width = max_width
                height = int(aspect_ratio * width)
                img = img.resize((width, height))
            
            # Convert the image to RGB mode
            img = img.convert('RGB')
            
            # Initialize the text art string
            text_art = size_tag
            
            # Iterate over each pixel and create a colored character
            pixels = list(img.getdata())
            for i, (r, g, b) in enumerate(pixels):
                # Generate TextMeshPro color tag in hexadecimal format
                hex_color = f"#{r:02X}{g:02X}{b:02X}"
                color_tag = f"<color={hex_color}>{pixel_char}</color>"
                
                text_art += color_tag
                
                # Add newline when reaching the width
                if (i + 1) % width == 0:
                    text_art += "\n"
            
            text_art += "</size>"
            return text_art
            
        except FileNotFoundError as e:
            raise FileError(f"Image file not found: {image_path}") from e
        except Exception as e:
            raise FileError(f"Failed to process image: {image_path}") from e
    
    @staticmethod
    def from_text(text: str, font_size: int = 20, color: str = "#FFFFFF") -> str:
        """
        Create styled text with TextMeshPro tags
        
        Args:
            text: The text to style
            font_size: The font size as a percentage
            color: The color for the text as a hex string
            
        Returns:
            Formatted text with TextMeshPro tags
        """
        return f"<size={font_size}%><color={color}>{text}</color></size>"
    
    @staticmethod
    def gradient_text(text: str, start_color: str = "#FF0000", 
                     end_color: str = "#0000FF", font_size: int = 20) -> str:
        """
        Create text with a color gradient
        
        Args:
            text: The text to apply gradient to
            start_color: Starting color (hex)
            end_color: Ending color (hex)
            font_size: Font size as percentage
            
        Returns:
            Text with character-by-character gradient coloring
        """
        # Convert hex colors to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        start_rgb = hex_to_rgb(start_color)
        end_rgb = hex_to_rgb(end_color)
        
        # Calculate step size for each color component
        steps = len(text) - 1
        if steps <= 0:
            return f"<size={font_size}%><color={start_color}>{text}</color></size>"
            
        r_step = (end_rgb[0] - start_rgb[0]) / steps
        g_step = (end_rgb[1] - start_rgb[1]) / steps
        b_step = (end_rgb[2] - start_rgb[2]) / steps
        
        # Build gradient text
        result = f"<size={font_size}%>"
        
        for i, char in enumerate(text):
            r = int(start_rgb[0] + r_step * i)
            g = int(start_rgb[1] + g_step * i)
            b = int(start_rgb[2] + b_step * i)
            
            hex_color = f"#{r:02X}{g:02X}{b:02X}"
            result += f"<color={hex_color}>{char}</color>"
        
        result += "</size>"
        return result
    
    @staticmethod
    def create_pattern(width: int, height: int, pattern_type: str = "checkerboard",
                     color1: str = "#FFFFFF", color2: str = "#000000") -> str:
        """
        Create a text art pattern
        
        Args:
            width: Width in characters
            height: Height in lines
            pattern_type: Type of pattern ("checkerboard", "horizontal", "vertical")
            color1: First color (hex)
            color2: Second color (hex)
            
        Returns:
            Text art pattern
        """
        result = "<size=20%>"
        
        for y in range(height):
            for x in range(width):
                if pattern_type == "checkerboard":
                    color = color1 if (x + y) % 2 == 0 else color2
                elif pattern_type == "horizontal":
                    color = color1 if y % 2 == 0 else color2
                elif pattern_type == "vertical":
                    color = color1 if x % 2 == 0 else color2
                else:
                    color = color1
                
                result += f"<color={color}>█</color>"
            result += "\n"
        
        result += "</size>"
        return result