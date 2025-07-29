#!/usr/bin/env python3
"""
Configuration management for imagpt.

Handles persistent configuration storage and validation using Pydantic.
Configuration is stored in a TOML file in the user's config directory.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Literal
import tomllib
import tomli_w
from pydantic import BaseModel, Field, field_validator


class ImageptConfig(BaseModel):
    """Configuration model for imagpt settings."""
    
    # API Configuration
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for image generation"
    )
    
    # Default Generation Settings
    default_model: Literal["gpt-image-1", "dall-e-2", "dall-e-3"] = Field(
        default="gpt-image-1",
        description="Default model to use for image generation"
    )
    
    default_size: Optional[str] = Field(
        default=None,
        description="Default image size (e.g., '1024x1024', '1536x1024')"
    )
    
    default_quality: Literal["auto", "high", "medium", "low", "hd", "standard"] = Field(
        default="high",
        description="Default image quality"
    )
    
    default_style: Optional[Literal["vivid", "natural"]] = Field(
        default=None,
        description="Default style for DALL-E 3 (vivid or natural)"
    )
    
    default_format: Literal["png", "jpeg", "webp"] = Field(
        default="png",
        description="Default output format"
    )
    
    # Image Processing Settings
    default_rescale: Optional[str] = Field(
        default=None,
        description="Default rescale size (e.g., '512x512', '800x600')"
    )
    
    default_crop_left: Optional[int] = Field(
        default=None,
        ge=0,
        description="Default left crop in pixels"
    )
    
    default_crop_right: Optional[int] = Field(
        default=None,
        ge=0,
        description="Default right crop in pixels"
    )
    
    default_crop_top: Optional[int] = Field(
        default=None,
        ge=0,
        description="Default top crop in pixels"
    )
    
    default_crop_bottom: Optional[int] = Field(
        default=None,
        ge=0,
        description="Default bottom crop in pixels"
    )
    
    # Directory Settings
    default_prompts_dir: Optional[str] = Field(
        default=None,
        description="Default directory to look for prompt files"
    )
    
    default_output_dir: Optional[str] = Field(
        default=None,
        description="Default directory to save generated images"
    )
    
    # Processing Settings
    default_delay: float = Field(
        default=2.0,
        ge=0.0,
        description="Default delay between API calls in seconds"
    )
    
    skip_existing: bool = Field(
        default=False,
        description="Default setting for skipping existing images"
    )

    # Default Watermark Settings
    default_watermark_image_path: Optional[str] = Field(
        default=None, 
        description="Default path to the watermark image."
    )
    default_watermark_position: Optional[Literal['topleft', 'topright', 'bottomleft', 'bottomright', 'center']] = Field(
        default='bottomright', 
        description="Default position for the watermark."
    )
    default_watermark_opacity: Optional[float] = Field(
        default=0.5, 
        ge=0.0, 
        le=1.0, 
        description="Default opacity for the watermark (0.0 to 1.0)."
    )
    
    @field_validator('default_size', 'default_rescale')
    @classmethod
    def validate_size(cls, v):
        """Validate image size format."""
        if v is None:
            return v
        
        if not isinstance(v, str):
            raise ValueError("Size must be a string")
        
        try:
            parts = v.split('x')
            if len(parts) != 2:
                raise ValueError("Size must be in format 'WIDTHxHEIGHT'")
            
            width, height = int(parts[0]), int(parts[1])
            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be positive integers")
                
        except ValueError as e:
            raise ValueError(f"Invalid size format '{v}': {e}")
        
        return v
    
    @field_validator('default_prompts_dir', 'default_output_dir', 'default_watermark_image_path')
    @classmethod
    def validate_paths(cls, v, info): # info is automatically passed by pydantic
        """Validate directory and file paths."""
        if v is None:
            return v
        
        path = Path(v).expanduser()

        if info.field_name == 'default_watermark_image_path':
            # For watermark image, it must be a file and exist
            if not path.exists():
                raise ValueError(f"Watermark image path does not exist: {path}")
            if not path.is_file():
                raise ValueError(f"Watermark image path is not a file: {path}")
        else: # For directories
            if not path.exists():
                raise ValueError(f"Directory does not exist: {path}")
            if not path.is_dir():
                raise ValueError(f"Path is not a directory: {path}")
        
        return str(path)

    @field_validator('default_watermark_opacity')
    @classmethod
    def validate_opacity(cls, v):
        """Validate opacity is between 0.0 and 1.0."""
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError("Opacity must be between 0.0 and 1.0")
        return v


class ConfigManager:
    """Manages persistent configuration and prompt library for imagpt."""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.toml"
        self.prompt_library_file = self._get_prompt_library_path()
        self._config: Optional[ImageptConfig] = None
        self._prompt_library: Optional[dict] = None
    
    def _get_config_dir(self) -> Path:
        """Get the configuration directory for the current platform."""
        if sys.platform == "win32":
            config_dir = Path(os.environ.get("APPDATA", "~")) / "imagpt"
        elif sys.platform == "darwin":
            config_dir = Path("~/Library/Application Support/imagpt").expanduser()
        else:
            # Linux and other Unix-like systems
            config_dir = Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser() / "imagpt"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def load_config(self) -> ImageptConfig:
        """Load configuration from file or create default."""
        if self._config is not None:
            return self._config
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'rb') as f:
                    config_data = tomllib.load(f)
                self._config = ImageptConfig(**config_data)
            except Exception as e:
                print(f"⚠️  Warning: Failed to load config from {self.config_file}: {e}")
                print("Using default configuration.")
                self._config = ImageptConfig()
        else:
            self._config = ImageptConfig()
        
        return self._config
    
    def save_config(self, config: ImageptConfig) -> None:
        """Save configuration to file."""
        try:
            config_data = config.model_dump(exclude_none=True)
            with open(self.config_file, 'wb') as f:
                tomli_w.dump(config_data, f)
            self._config = config
            print(f"✅ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
            raise
    
    def update_config(self, **kwargs) -> ImageptConfig:
        """Update configuration with new values."""
        config = self.load_config()
        
        # Create a new config with updated values
        config_data = config.model_dump()
        config_data.update(kwargs)
        
        try:
            new_config = ImageptConfig(**config_data)
            self.save_config(new_config)
            return new_config
        except Exception as e:
            print(f"❌ Failed to update configuration: {e}")
            raise
    
    def reset_config(self) -> ImageptConfig:
        """Reset configuration to defaults."""
        config = ImageptConfig()
        self.save_config(config)
        return config
    
    def show_config(self) -> None:
        """Display current configuration."""
        config = self.load_config()
        
        print("🔧 Current Configuration")
        print("=" * 50)
        
        # API Settings
        print("\n📡 API Settings:")
        api_key = config.openai_api_key
        if api_key:
            masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
            print(f"  OpenAI API Key: {masked_key}")
        else:
            print("  OpenAI API Key: Not set")
        
        # Generation Settings
        print("\n🎨 Generation Settings:")
        print(f"  Default Model: {config.default_model}")
        print(f"  Default Size: {config.default_size or 'Auto (model-dependent)'}")
        print(f"  Default Quality: {config.default_quality}")
        print(f"  Default Style: {config.default_style or 'None'}")
        print(f"  Default Format: {config.default_format}")
        
        # Image Processing Settings
        print("\n🖼️ Image Processing Settings:")
        print(f"  Default Rescale: {config.default_rescale or 'None'}")
        print(f"  Default Crop Left: {config.default_crop_left or 'None'}")
        print(f"  Default Crop Right: {config.default_crop_right or 'None'}")
        print(f"  Default Crop Top: {config.default_crop_top or 'None'}")
        print(f"  Default Crop Bottom: {config.default_crop_bottom or 'None'}")
        
        # Directory Settings
        print("\n📁 Directory Settings:")
        print(f"  Default Prompts Dir: {config.default_prompts_dir or 'None'}")
        print(f"  Default Output Dir: {config.default_output_dir or 'None'}")
        
        # Processing Settings
        print("\n⚙️  Processing Settings:")
        print(f"  Default Delay: {config.default_delay}s")
        print(f"  Skip Existing: {config.skip_existing}")

        # Watermark Settings
        print("\n💧 Watermark Settings:")
        print(f"  Default Watermark Image Path: {config.default_watermark_image_path or 'None'}")
        print(f"  Default Watermark Position: {config.default_watermark_position or 'None'}")
        print(f"  Default Watermark Opacity: {config.default_watermark_opacity if config.default_watermark_opacity is not None else 'None'}")
        
        print(f"\n📄 Config File: {self.config_file}")
        print(f"📚 Prompt Library File: {self.prompt_library_file}")

    def get_api_key(self) -> str:
        """Get API key from config or environment."""
        config = self.load_config()
        
        # Try config first, then environment
        api_key = config.openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print("❌ Error: OpenAI API key not found")
            print("Set it using one of these methods:")
            print("1. imagpt config set openai_api_key 'your-key-here'")
            print("2. export OPENAI_API_KEY='your-key-here'")
            sys.exit(1)
        
        return api_key


# Global config manager instance
config_manager = ConfigManager()

    # --- Prompt Library Management Methods ---

    def _get_prompt_library_path(self) -> Path:
        """Helper method to return the prompt library file path."""
        return self.config_dir / "prompt_library.toml"

    def load_prompt_library(self) -> dict:
        """
        Reads the TOML file from _get_prompt_library_path().
        Returns a dictionary of prompts (e.g., {'prompt_name': {details...}}).
        """
        if self._prompt_library is not None: # Use cached if available
            return self._prompt_library

        if not self.prompt_library_file.exists():
            self._prompt_library = {} # Default empty library structure
            return self._prompt_library
        
        try:
            with open(self.prompt_library_file, 'rb') as f:
                data = tomllib.load(f)
            # The prompts are expected under a top-level "prompts" table
            self._prompt_library = data.get("prompts", {})
            return self._prompt_library
        except tomllib.TOMLDecodeError as e:
            print(f"⚠️ Warning: Error decoding prompt library file {self.prompt_library_file}: {e}")
            self._prompt_library = {} # Return empty on error
            return self._prompt_library
        except Exception as e:
            print(f"⚠️ Warning: Failed to load prompt library from {self.prompt_library_file}: {e}")
            self._prompt_library = {}
            return self._prompt_library

    def save_prompt_library(self, library_data: dict) -> None:
        """
        Writes the library_data (prompts) to the TOML file.
        The data is stored under a top-level "prompts" table.
        """
        try:
            # Wrap the library_data under a "prompts" key for saving
            to_save = {"prompts": library_data}
            with open(self.prompt_library_file, 'wb') as f:
                tomli_w.dump(to_save, f)
            self._prompt_library = library_data # Update cache
            print(f"📚 Prompt library saved to {self.prompt_library_file}")
        except Exception as e:
            print(f"❌ Failed to save prompt library: {e}")
            raise

    def add_prompt_to_library(self, name: str, prompt_attributes: dict) -> bool:
        """
        Adds or updates a prompt in the library. Overwrites if name exists.
        Returns True on success.
        """
        # Validate prompt_attributes (ensure only allowed keys are present)
        allowed_keys = {
            "text", "model", "size", "quality", "style", 
            "watermark_image_path", "watermark_position", "watermark_opacity",
            "format", "rescale", "crop_left", "crop_right", "crop_top", "crop_bottom" # Added generation/processing keys
        }
        validated_attributes = {k: v for k, v in prompt_attributes.items() if k in allowed_keys and v is not None}
        if not validated_attributes.get("text"): # Prompt text is mandatory
            print("❌ Error: Prompt text is required to save to library.")
            return False

        library = self.load_prompt_library() # Load current library
        library[name] = validated_attributes # Add or overwrite
        try:
            self.save_prompt_library(library)
            return True
        except Exception:
            return False

    def get_prompt_from_library(self, name: str) -> Optional[dict]:
        """
        Retrieves a prompt by name from the library.
        Returns the prompt attributes dictionary or None if not found.
        """
        library = self.load_prompt_library()
        return library.get(name)

    def remove_prompt_from_library(self, name: str) -> bool:
        """
        Removes a prompt by name from the library.
        Returns True if removed, False if not found.
        """
        library = self.load_prompt_library()
        if name in library:
            del library[name]
            try:
                self.save_prompt_library(library)
                return True
            except Exception:
                return False
        return False

    def list_library_prompts(self) -> dict:
        """
        Returns the entire prompt library.
        """
        return self.load_prompt_library()