#!/usr/bin/env python3
"""
FastMCP server for imagpt - AI Image Generator

This module provides MCP (Model Context Protocol) server functionality for the imagpt tool,
allowing LLMs to generate images using OpenAI's API through standardized MCP tools.
"""

import os
import base64
import time
from pathlib import Path
from typing import Optional, List, Literal
import tempfile

import openai
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .config import config_manager
from .cli import (
    generate_image, 
    save_image, 
    read_prompt_file, 
    find_prompt_files,
    get_output_path,
    validate_model_size,
    get_default_size
)
from .image_processing import apply_watermark # Added import

# Initialize FastMCP server
mcp = FastMCP("imagpt", description="🎨 AI Image Generator - Generate images using OpenAI API")


class ImageGenerationRequest(BaseModel):
    """Request model for image generation."""
    prompt: str = Field(description="Text prompt for image generation")
    model: Literal["gpt-image-1", "dall-e-2", "dall-e-3"] = Field(
        default="gpt-image-1", 
        description="Model to use for image generation"
    )
    size: Optional[str] = Field(
        default=None, 
        description="Image size (e.g., '1024x1024', '1536x1024', '1024x1536')"
    )
    quality: Literal["auto", "high", "medium", "low", "hd", "standard"] = Field(
        default="high", 
        description="Image quality"
    )
    style: Optional[Literal["vivid", "natural"]] = Field(
        default=None, 
        description="Image style for DALL-E 3 (vivid or natural)"
    )
    output_format: Literal["png", "jpeg", "webp"] = Field(
        default="png", 
        description="Output format"
    )
    rescale: Optional[str] = Field(
        default=None,
        description="Rescale image to size (e.g., '512x512', '800x600')"
    )
    crop_left: Optional[int] = Field(
        default=None,
        ge=0,
        description="Crop pixels from left edge"
    )
    crop_right: Optional[int] = Field(
        default=None,
        ge=0,
        description="Crop pixels from right edge"
    )
    crop_top: Optional[int] = Field(
        default=None,
        ge=0,
        description="Crop pixels from top edge"
    )
    crop_bottom: Optional[int] = Field(
        default=None,
        ge=0,
        description="Crop pixels from bottom edge"
    )
    filename: Optional[str] = Field(
        default=None, 
        description="Optional filename for the generated image"
    )
    # Watermark fields for ImageGenerationRequest
    watermark_image_data: Optional[str] = Field(None, description="Base64 encoded string of the watermark image.")
    watermark_position: Optional[Literal['topleft', 'topright', 'bottomleft', 'bottomright', 'center']] = Field(None, description="Position for the watermark.")
    watermark_opacity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Opacity for the watermark (0.0 to 1.0).")
    watermark_scale: Optional[float] = Field(None, ge=0.0, description="Scale for the watermark relative to base image size.")
    watermark_padding: Optional[int] = Field(None, ge=0, description="Padding for the watermark in pixels.")


class BatchGenerationRequest(BaseModel):
    """Request model for batch image generation from directory."""
    prompts_dir: str = Field(description="Directory containing prompt files (.prompt, .txt, .md)")
    output_dir: Optional[str] = Field(
        default=None, 
        description="Output directory for generated images (defaults to prompts_dir)"
    )
    model: Literal["gpt-image-1", "dall-e-2", "dall-e-3"] = Field(
        default="gpt-image-1", 
        description="Model to use for image generation"
    )
    size: Optional[str] = Field(
        default=None, 
        description="Image size (e.g., '1024x1024', '1536x1024', '1024x1536')"
    )
    quality: Literal["auto", "high", "medium", "low", "hd", "standard"] = Field(
        default="high", 
        description="Image quality"
    )
    style: Optional[Literal["vivid", "natural"]] = Field(
        default=None, 
        description="Image style for DALL-E 3 (vivid or natural)"
    )
    output_format: Literal["png", "jpeg", "webp"] = Field(
        default="png", 
        description="Output format"
    )
    rescale: Optional[str] = Field(
        default=None,
        description="Rescale image to size (e.g., '512x512', '800x600')"
    )
    crop_left: Optional[int] = Field(
        default=None,
        ge=0,
        description="Crop pixels from left edge"
    )
    crop_right: Optional[int] = Field(
        default=None,
        ge=0,
        description="Crop pixels from right edge"
    )
    crop_top: Optional[int] = Field(
        default=None,
        ge=0,
        description="Crop pixels from top edge"
    )
    crop_bottom: Optional[int] = Field(
        default=None,
        ge=0,
        description="Crop pixels from bottom edge"
    )
    delay: float = Field(
        default=2.0, 
        ge=0.0, 
        description="Delay between API calls in seconds"
    )
    skip_existing: bool = Field(
        default=False, 
        description="Skip generating images that already exist"
    )


class ImageEditRequest(BaseModel):
    """Request model for image editing or creating variations."""
    image_data: str = Field(description="Base64 encoded string of the source image.")
    prompt: Optional[str] = Field(None, description="Text prompt for the edit. If None, a variation is created.")
    mask_data: Optional[str] = Field(None, description="Base64 encoded string of the mask image (PNG).")
    model: Optional[Literal["gpt-image-1", "dall-e-2"]] = Field(None, description="Model to use. 'dall-e-2' for variations or edits, 'gpt-image-1' for edits.")
    n: int = Field(default=1, ge=1, le=10, description="Number of images to generate.")
    size: Optional[str] = Field(None, description="Image size (e.g., '1024x1024').")
    quality: Optional[Literal["auto", "high", "medium", "low", "standard"]] = Field(None, description="Image quality. For gpt-image-1 edits (low, medium, high). 'standard' for dall-e-2 (implicit).")
    background: Optional[Literal["transparent", "opaque", "auto"]] = Field(None, description="Background for gpt-image-1 edits.")
    response_format: Optional[Literal["url", "b64_json"]] = Field(None, description="Response format for dall-e-2 (url or b64_json). gpt-image-1 always returns b64_json.")
    output_filename_base: Optional[str] = Field(None, description="Optional base name for output file(s). Extension and suffixes will be added.")
    output_format: Literal["png", "jpeg", "webp"] = Field(default="png", description="Format to save the image as.")
    # Watermark fields for ImageEditRequest
    watermark_image_data: Optional[str] = Field(None, description="Base64 encoded string of the watermark image.")
    watermark_position: Optional[Literal['topleft', 'topright', 'bottomleft', 'bottomright', 'center']] = Field(None, description="Position for the watermark.")
    watermark_opacity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Opacity for the watermark (0.0 to 1.0).")
    watermark_scale: Optional[float] = Field(None, ge=0.0, description="Scale for the watermark relative to base image size.")
    watermark_padding: Optional[int] = Field(None, ge=0, description="Padding for the watermark in pixels.")


@mcp.tool()
def generate_single_image(request: ImageGenerationRequest) -> str:
    """
    Generate a single image from a text prompt using OpenAI's API.
    
    Returns the path to the generated image file.
    """
    temp_watermark_path = None
    try:
        # Load configuration and apply defaults
        config = config_manager.load_config()
        
        # Apply configuration defaults if not specified
        model = request.model
        size = request.size or config.default_size or get_default_size(model)
        quality = request.quality
        style = request.style or config.default_style
        output_format = request.output_format
        rescale = request.rescale or config.default_rescale
        crop_left = request.crop_left if request.crop_left is not None else config.default_crop_left
        crop_right = request.crop_right if request.crop_right is not None else config.default_crop_right
        crop_top = request.crop_top if request.crop_top is not None else config.default_crop_top
        crop_bottom = request.crop_bottom if request.crop_bottom is not None else config.default_crop_bottom
        
        # Validate model and size compatibility
        if not validate_model_size(model, size):
            valid_sizes = {
                "gpt-image-1": ["1024x1024", "1536x1024", "1024x1536"],
                "dall-e-2": ["256x256", "512x512", "1024x1024"],
                "dall-e-3": ["1024x1024", "1792x1024", "1024x1792"]
            }
            raise ValueError(f"Size '{size}' is not valid for model '{model}'. Valid sizes: {', '.join(valid_sizes[model])}")
        
        # Initialize OpenAI client
        api_key = config_manager.get_api_key()
        client = openai.OpenAI(api_key=api_key)
        
        # Generate filename if not provided
        if request.filename:
            filename = request.filename
            if not filename.endswith(f".{output_format}"):
                filename = f"{filename}.{output_format}"
        else:
            # Generate filename from prompt
            safe_name = "".join(c for c in request.prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_').lower()
            filename = f"{safe_name}.{output_format}"
        
        # Use temporary directory for output
        temp_dir = Path(tempfile.gettempdir()) / "imagpt_mcp"
        temp_dir.mkdir(exist_ok=True)
        output_path = temp_dir / filename
        
        # Generate image
        image_data = generate_image(
            client, request.prompt, filename, 
            model, size, quality, style, output_format
        )
        
        # Save image
        save_image(
            image_data, output_path, rescale, crop_left, crop_right, 
            crop_top, crop_bottom, output_format
            # No watermark params passed to initial save_image here for MCP single generation
        )

        # --- Watermarking Step ---
        current_watermark_path_to_use = None
        if request.watermark_image_data:
            try:
                watermark_bytes = base64.b64decode(request.watermark_image_data)
                # Use a unique name for temp watermark to avoid clashes if multiple calls happen
                temp_watermark_path = temp_dir / f"temp_watermark_{os.urandom(4).hex()}.png"
                with open(temp_watermark_path, "wb") as f_wm:
                    f_wm.write(watermark_bytes)
                current_watermark_path_to_use = str(temp_watermark_path)
            except Exception as b64_e:
                print(f"⚠️ Warning: Could not decode/save base64 watermark image data: {b64_e}. Skipping watermark.")
        else:
            current_watermark_path_to_use = config.default_watermark_image_path
        
        if current_watermark_path_to_use:
            try:
                generated_image_bytes = output_path.read_bytes()
                wm_params = {}
                if request.watermark_position is not None: wm_params['position'] = request.watermark_position
                elif config.default_watermark_position is not None: wm_params['position'] = config.default_watermark_position
                
                if request.watermark_opacity is not None: wm_params['opacity'] = request.watermark_opacity
                elif config.default_watermark_opacity is not None: wm_params['opacity'] = config.default_watermark_opacity

                if request.watermark_scale is not None: wm_params['scale'] = request.watermark_scale
                # No default scale in config, apply_watermark has its own default if not provided

                if request.watermark_padding is not None: wm_params['padding'] = request.watermark_padding
                # No default padding in config, apply_watermark has its own default
                
                print(f"💧 Applying watermark to MCP generated image: {output_path} using {current_watermark_path_to_use}")
                final_image_bytes = apply_watermark(
                    generated_image_bytes, 
                    current_watermark_path_to_use,
                    target_format=output_format, # Use the request's output_format
                    **wm_params
                )
                output_path.write_bytes(final_image_bytes)
                print(f"✅ Watermark applied successfully to {output_path}")
            except FileNotFoundError:
                 print(f"⚠️ Watermark image not found at '{current_watermark_path_to_use}'. Skipping watermark.")
            except Exception as wm_e:
                print(f"⚠️ Error applying watermark: {wm_e}. Skipping watermark.")
        # --- End Watermarking Step ---

        return f"✅ Image generated successfully: {output_path}"
        
    except Exception as e:
        return f"❌ Error generating image: {str(e)}"
    finally:
        if temp_watermark_path and temp_watermark_path.exists():
            try:
                temp_watermark_path.unlink()
            except Exception as e_clean:
                print(f"⚠️ Warning: Failed to clean up temporary watermark file {temp_watermark_path}: {e_clean}")


@mcp.tool()
def generate_batch_images(request: BatchGenerationRequest) -> str:
    """
    Generate images from all prompt files in a directory.
    
    Processes .prompt, .txt, and .md files and generates corresponding images.
    """
    try:
        # Load configuration
        config = config_manager.load_config()
        
        # Validate directories
        prompts_dir = Path(request.prompts_dir)
        if not prompts_dir.exists():
            return f"❌ Prompts directory does not exist: {prompts_dir}"
        
        if not prompts_dir.is_dir():
            return f"❌ Prompts path is not a directory: {prompts_dir}"
        
        output_dir = Path(request.output_dir) if request.output_dir else prompts_dir
        
        # Apply configuration defaults
        model = request.model
        size = request.size or config.default_size or get_default_size(model)
        quality = request.quality
        style = request.style or config.default_style
        output_format = request.output_format
        rescale = request.rescale or config.default_rescale
        crop_left = request.crop_left if request.crop_left is not None else config.default_crop_left
        crop_right = request.crop_right if request.crop_right is not None else config.default_crop_right
        crop_top = request.crop_top if request.crop_top is not None else config.default_crop_top
        crop_bottom = request.crop_bottom if request.crop_bottom is not None else config.default_crop_bottom
        
        # Validate model and size compatibility
        if not validate_model_size(model, size):
            valid_sizes = {
                "gpt-image-1": ["1024x1024", "1536x1024", "1024x1536"],
                "dall-e-2": ["256x256", "512x512", "1024x1024"],
                "dall-e-3": ["1024x1024", "1792x1024", "1024x1792"]
            }
            return f"❌ Size '{size}' is not valid for model '{model}'. Valid sizes: {', '.join(valid_sizes[model])}"
        
        # Initialize OpenAI client
        api_key = config_manager.get_api_key()
        client = openai.OpenAI(api_key=api_key)
        
        # Find all prompt files
        prompt_files = find_prompt_files(prompts_dir)
        if not prompt_files:
            return f"❌ No prompt files found in {prompts_dir}. Looking for files with extensions: .prompt, .txt, .md"
        
        results = []
        success_count = 0
        
        # Generate images for each prompt file
        for prompt_file in prompt_files:
            try:
                output_path = get_output_path(prompt_file, output_dir, output_format)
                
                # Skip if image already exists and skip_existing is set
                if request.skip_existing and output_path.exists():
                    results.append(f"⏭️  Skipped {prompt_file.name} (image already exists)")
                    continue
                
                # Read prompt
                file_prompt = read_prompt_file(prompt_file)
                if not file_prompt.strip():
                    results.append(f"⚠️  Skipped {prompt_file.name} (empty prompt)")
                    continue
                
                # Generate image
                image_data = generate_image(
                    client, file_prompt, prompt_file.name, 
                    model, size, quality, style, output_format
                )
                
                # Save image
                save_image(
                    image_data, output_path, rescale, crop_left, crop_right, 
                    crop_top, crop_bottom, output_format
                )
                results.append(f"✅ Generated: {prompt_file.name} -> {output_path.name}")
                success_count += 1
                
                # Rate limiting
                if request.delay > 0:
                    time.sleep(request.delay)
                
            except Exception as e:
                results.append(f"❌ Failed to process {prompt_file.name}: {e}")
                continue
        
        summary = f"\n🎉 Batch generation complete! Successfully generated {success_count}/{len(prompt_files)} images"
        summary += f"\n📂 Images saved to: {output_dir}"
        
        return "\n".join(results) + summary
        
    except Exception as e:
        return f"❌ Error in batch generation: {str(e)}"


@mcp.tool()
def list_prompt_files(directory: str) -> str:
    """
    List all prompt files in a directory.
    
    Shows available .prompt, .txt, and .md files that can be processed.
    """
    try:
        prompts_dir = Path(directory)
        if not prompts_dir.exists():
            return f"❌ Directory does not exist: {prompts_dir}"
        
        if not prompts_dir.is_dir():
            return f"❌ Path is not a directory: {prompts_dir}"
        
        prompt_files = find_prompt_files(prompts_dir)
        
        if not prompt_files:
            return f"📁 No prompt files found in {prompts_dir}\nLooking for files with extensions: .prompt, .txt, .md"
        
        results = [f"📁 Found {len(prompt_files)} prompt files in {prompts_dir}:"]
        for prompt_file in prompt_files:
            # Try to read a preview of the prompt
            try:
                content = read_prompt_file(prompt_file)
                preview = content[:100] + "..." if len(content) > 100 else content
                results.append(f"  📄 {prompt_file.name}: {preview}")
            except Exception:
                results.append(f"  📄 {prompt_file.name}: (unable to read)")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"❌ Error listing prompt files: {str(e)}"


@mcp.tool()
def show_config() -> str:
    """
    Show current imagpt configuration settings.
    
    Displays API settings, generation defaults, and directory settings.
    """
    try:
        config = config_manager.load_config()
        
        results = ["🔧 Current imagpt Configuration", "=" * 50]
        
        # API Settings
        results.append("\n📡 API Settings:")
        api_key = config.openai_api_key
        if api_key:
            masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
            results.append(f"  OpenAI API Key: {masked_key}")
        else:
            results.append("  OpenAI API Key: Not set")
        
        # Generation Settings
        results.append("\n🎨 Generation Settings:")
        results.append(f"  Default Model: {config.default_model}")
        results.append(f"  Default Size: {config.default_size or 'Auto (model-dependent)'}")
        results.append(f"  Default Quality: {config.default_quality}")
        results.append(f"  Default Style: {config.default_style or 'None'}")
        results.append(f"  Default Format: {config.default_format}")
        
        # Image Processing Settings
        results.append("\n🖼️ Image Processing Settings:")
        results.append(f"  Default Rescale: {config.default_rescale or 'None'}")
        results.append(f"  Default Crop Left: {config.default_crop_left or 'None'}")
        results.append(f"  Default Crop Right: {config.default_crop_right or 'None'}")
        results.append(f"  Default Crop Top: {config.default_crop_top or 'None'}")
        results.append(f"  Default Crop Bottom: {config.default_crop_bottom or 'None'}")
        
        # Directory Settings
        results.append("\n📁 Directory Settings:")
        results.append(f"  Default Prompts Dir: {config.default_prompts_dir or 'None'}")
        results.append(f"  Default Output Dir: {config.default_output_dir or 'None'}")
        
        # Processing Settings
        results.append("\n⚙️  Processing Settings:")
        results.append(f"  Default Delay: {config.default_delay}s")
        results.append(f"  Skip Existing: {config.skip_existing}")
        
        results.append(f"\n📄 Config File: {config_manager.config_file}")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"❌ Error showing configuration: {str(e)}"


@mcp.tool()
def update_config(key: str, value: str) -> str:
    """
    Update a configuration setting.
    
    Available keys: openai_api_key, default_model, default_size, default_quality, 
    default_style, default_format, default_rescale, default_crop_left, default_crop_right,
    default_crop_top, default_crop_bottom, default_prompts_dir, default_output_dir, 
    default_delay, skip_existing
    """
    try:
        # Convert string values to appropriate types
        if key in ["default_delay"]:
            value = float(value)
        elif key in ["skip_existing"]:
            value = value.lower() in ["true", "1", "yes", "on"]
        elif key in ["default_crop_left", "default_crop_right", "default_crop_top", "default_crop_bottom"]:
            value = int(value) if value.lower() != "none" else None
        
        config_manager.update_config(**{key: value})
        return f"✅ Set {key} = {value}"
        
    except Exception as e:
        return f"❌ Failed to set configuration: {str(e)}"


def main():
    """Main entry point for the MCP server."""
    mcp.run()


@mcp.tool()
def edit_or_vary_image(request: ImageEditRequest) -> str:
    """
    Edit an image based on a prompt or create variations of it.
    Uses temporary files for processing and returns paths to generated images.
    """
    request_temp_dir = None
    source_image_path = None
    mask_image_path = None
    temp_watermark_path_for_request = None # For cleaning up

    try:
        config = config_manager.load_config()
        api_key = config_manager.get_api_key()
        client = openai.OpenAI(api_key=api_key)

        request_temp_dir = Path(tempfile.mkdtemp(prefix="imagpt_mcp_edit_"))

        # Decode and save source image
        image_bytes = base64.b64decode(request.image_data)
        source_filename_base = request.output_filename_base or "source_image_mcp"
        source_image_path = request_temp_dir / f"{source_filename_base}_input.{request.output_format}"
        with open(source_image_path, "wb") as f:
            f.write(image_bytes)

        # Decode and save mask image if provided
        if request.mask_data:
            mask_bytes = base64.b64decode(request.mask_data)
            mask_image_path = request_temp_dir / "mask_image_mcp.png" # Mask is expected to be PNG
            with open(mask_image_path, "wb") as f:
                f.write(mask_bytes)

        is_variation = not request.prompt
        api_params = {}

        # Determine effective model
        if is_variation:
            effective_model = "dall-e-2"
            if request.model and request.model != "dall-e-2":
                # Log warning if possible, or just override
                pass
        else: # Edit
            effective_model = request.model or config.default_model or "dall-e-2"
            if effective_model not in ["dall-e-2", "gpt-image-1"]:
                 raise ValueError(f"Unsupported model for edit: {effective_model}. Choose 'dall-e-2' or 'gpt-image-1'.")


        # Determine effective size
        effective_size = request.size or config.default_size or get_default_size(effective_model)
        if not validate_model_size(effective_model, effective_size):
            # Provide valid sizes based on the actual model being used for the operation
            # This logic might need refinement if get_default_size/validate_model_size aren't perfectly aligned
            # with edit/variation specific model constraints. For now, assume they are sufficient.
            if effective_model == "dall-e-2":
                valid_sizes_list = ["256x256", "512x512", "1024x1024"]
            elif effective_model == "gpt-image-1": # Edits
                 valid_sizes_list = ["1024x1024", "1536x1024", "1024x1536"] # Example, check docs
            else: # Should not happen due to earlier check
                valid_sizes_list = ["N/A"]
            raise ValueError(f"Size '{effective_size}' is not valid for model '{effective_model}'. Valid sizes: {', '.join(valid_sizes_list)}")

        api_params["n"] = request.n
        api_params["size"] = effective_size

        response_data = []

        with open(source_image_path, "rb") as f_image:
            api_params["image"] = f_image

            if is_variation:
                api_params["model"] = "dall-e-2" # Always dall-e-2 for variations
                api_params["response_format"] = request.response_format or "b64_json"
                response = client.images.create_variation(**api_params)
                response_data = response.data
            else: # Edit
                api_params["prompt"] = request.prompt
                api_params["model"] = effective_model

                if mask_image_path:
                    with open(mask_image_path, "rb") as f_mask:
                        api_params["mask"] = f_mask
                        if effective_model == "gpt-image-1":
                            if request.quality and request.quality not in ["auto", "standard"]:
                                api_params["quality"] = request.quality
                            if request.background:
                                api_params["background"] = request.background
                            # gpt-image-1 implies b64_json
                        else: # dall-e-2 edit
                            api_params["response_format"] = request.response_format or "b64_json"
                        response = client.images.edit(**api_params)
                        response_data = response.data
                else: # No mask
                    if effective_model == "gpt-image-1":
                        if request.quality and request.quality not in ["auto", "standard"]:
                             api_params["quality"] = request.quality
                        if request.background:
                            api_params["background"] = request.background
                        # gpt-image-1 implies b64_json
                    else: # dall-e-2 edit
                        api_params["response_format"] = request.response_format or "b64_json"
                    response = client.images.edit(**api_params)
                    response_data = response.data
        
        output_paths = []
        for i, image_object in enumerate(response_data):
            image_data_bytes = None
            # Prioritize b64_json
            if hasattr(image_object, "b64_json") and image_object.b64_json:
                image_data_bytes = base64.b64decode(image_object.b64_json)
            elif hasattr(image_object, "url") and image_object.url:
                # Only download if URL is the only option or specifically requested for dall-e-2
                if (effective_model == "dall-e-2" and request.response_format == "url") or not image_data_bytes:
                    try:
                        import httpx
                        http_response = httpx.get(image_object.url)
                        http_response.raise_for_status()
                        image_data_bytes = http_response.content
                    except Exception as http_e:
                        # Log this error and continue if possible, or append to a list of errors
                        print(f"Warning: Failed to download image from URL {image_object.url}: {http_e}")
                        continue # Skip this image
            
            if not image_data_bytes:
                print(f"Warning: No image data could be retrieved for image {i+1}. Skipping.")
                continue

            base_name = request.output_filename_base or ("image_edit" if not is_variation else "image_variation")
            suffix = f"_{i}" if request.n > 1 or (request.n == 1 and not request.output_filename_base) else ""
            
            # Ensure the output path has the correct extension from request.output_format
            current_output_filename = f"{base_name}{suffix}.{request.output_format}"
            current_output_path = request_temp_dir / current_output_filename
            
            save_image(image_data_bytes, current_output_path, output_format=request.output_format)
            output_paths.append(str(current_output_path))

        if not output_paths:
            return "❌ No images were successfully generated or saved."
        return f"✅ Images generated: {', '.join(output_paths)}"

    except openai.APIError as e:
        # Specific handling for API errors
        return f"❌ OpenAI API Error: {str(e)}"
    except ValueError as e: # For custom validation errors
        return f"❌ Validation Error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected Error in edit_or_vary_image: {str(e)}"
    finally:
        # Cleanup temporary watermark if created from base64 data
        if temp_watermark_path_for_request and temp_watermark_path_for_request.exists():
            try:
                temp_watermark_path_for_request.unlink()
            except Exception as e_clean:
                 print(f"⚠️ Warning: Failed to clean up temporary watermark for edit request: {e_clean}")
    # No explicit cleanup of request_temp_dir itself needed here, as OS typically handles /tmp.

@mcp.tool() # This was missing the decorator in the diff
def edit_or_vary_image(request: ImageEditRequest) -> str: # Definition was duplicated, this is the corrected one
    """
    Edit an image based on a prompt or create variations of it.
    Uses temporary files for processing and returns paths to generated images.
    """
    request_temp_dir = None
    source_image_path = None
    mask_image_path = None
    temp_watermark_path_for_request = None

    try:
        config = config_manager.load_config()
        api_key = config_manager.get_api_key()
        client = openai.OpenAI(api_key=api_key)

        request_temp_dir = Path(tempfile.mkdtemp(prefix="imagpt_mcp_edit_"))

        image_bytes = base64.b64decode(request.image_data)
        source_filename_base = request.output_filename_base or "source_image_mcp"
        # Use request.output_format for the initially saved source image to determine its type
        source_image_path = request_temp_dir / f"{source_filename_base}_input.{request.output_format}"
        with open(source_image_path, "wb") as f:
            f.write(image_bytes)

        if request.mask_data:
            mask_bytes = base64.b64decode(request.mask_data)
            mask_image_path = request_temp_dir / "mask_image_mcp.png"
            with open(mask_image_path, "wb") as f:
                f.write(mask_bytes)

        is_variation = not request.prompt
        api_params = {}

        if is_variation:
            effective_model = "dall-e-2"
        else:
            effective_model = request.model or config.default_model or "dall-e-2"
            if effective_model not in ["dall-e-2", "gpt-image-1"]:
                 raise ValueError(f"Unsupported model for edit: {effective_model}.")
        
        effective_size = request.size or config.default_size or get_default_size(effective_model)
        if not validate_model_size(effective_model, effective_size):
            valid_sizes_list = ["256x256", "512x512", "1024x1024"] if effective_model == "dall-e-2" else ["1024x1024", "1536x1024", "1024x1536"]
            raise ValueError(f"Size '{effective_size}' is not valid for model '{effective_model}'. Valid: {', '.join(valid_sizes_list)}")

        api_params["n"] = request.n
        api_params["size"] = effective_size
        response_data_objects = []

        with open(source_image_path, "rb") as f_image:
            api_params["image"] = f_image
            if is_variation:
                api_params["model"] = "dall-e-2"
                api_params["response_format"] = request.response_format or "b64_json"
                response = client.images.create_variation(**api_params)
                response_data_objects = response.data
            else: # Edit
                api_params["prompt"] = request.prompt
                api_params["model"] = effective_model
                opened_mask_file = None
                try:
                    if mask_image_path:
                        opened_mask_file = open(mask_image_path, "rb")
                        api_params["mask"] = opened_mask_file
                    
                    if effective_model == "gpt-image-1":
                        if request.quality and request.quality not in ["auto", "standard"]: api_params["quality"] = request.quality
                        if request.background: api_params["background"] = request.background
                    else: # dall-e-2 edit
                        api_params["response_format"] = request.response_format or "b64_json"
                    response = client.images.edit(**api_params)
                    response_data_objects = response.data
                finally:
                    if opened_mask_file: opened_mask_file.close()
        
        processed_output_paths = []
        for i, image_object in enumerate(response_data_objects):
            image_data_bytes = None
            if hasattr(image_object, "b64_json") and image_object.b64_json:
                image_data_bytes = base64.b64decode(image_object.b64_json)
            elif hasattr(image_object, "url") and image_object.url:
                if (effective_model == "dall-e-2" and (request.response_format or "b64_json") == "url"):
                    try:
                        import httpx
                        http_response = httpx.get(image_object.url)
                        http_response.raise_for_status()
                        image_data_bytes = http_response.content
                    except Exception as http_e:
                        print(f"Warning: Failed to download image from URL {image_object.url}: {http_e}")
                        continue
            
            if not image_data_bytes:
                print(f"Warning: No image data for image {i+1}. Skipping.")
                continue

            base_name = request.output_filename_base or ("image_edit" if not is_variation else "image_variation")
            suffix = f"_{i}" if request.n > 1 or (request.n == 1 and not request.output_filename_base) else ""
            current_output_filename = f"{base_name}{suffix}.{request.output_format}"
            current_output_path = request_temp_dir / current_output_filename
            
            # Save initially generated/edited image (before potential watermark)
            # save_image is complex, for MCP we just write bytes here
            with open(current_output_path, "wb") as f_out:
                f_out.write(image_data_bytes)
            processed_output_paths.append(str(current_output_path))

        # --- Watermarking Step for edit_or_vary_image ---
        current_watermark_path_to_use_for_edit = None
        if request.watermark_image_data:
            try:
                watermark_bytes = base64.b64decode(request.watermark_image_data)
                temp_watermark_path_for_request = request_temp_dir / f"mcp_edit_temp_watermark_{os.urandom(4).hex()}.png"
                with open(temp_watermark_path_for_request, "wb") as f_wm:
                    f_wm.write(watermark_bytes)
                current_watermark_path_to_use_for_edit = str(temp_watermark_path_for_request)
            except Exception as b64_e:
                print(f"⚠️ Warning: Could not decode/save base64 watermark for edit request: {b64_e}. Skipping watermark.")
        else:
            current_watermark_path_to_use_for_edit = config.default_watermark_image_path

        if current_watermark_path_to_use_for_edit and processed_output_paths:
            print(f"💧 Applying watermark to {len(processed_output_paths)} edited/varied image(s) using {current_watermark_path_to_use_for_edit}...")
            for saved_path_str in processed_output_paths:
                saved_path_obj = Path(saved_path_str)
                try:
                    img_bytes_to_watermark = saved_path_obj.read_bytes()
                    wm_params_edit = {}
                    if request.watermark_position is not None: wm_params_edit['position'] = request.watermark_position
                    elif config.default_watermark_position is not None: wm_params_edit['position'] = config.default_watermark_position
                    
                    if request.watermark_opacity is not None: wm_params_edit['opacity'] = request.watermark_opacity
                    elif config.default_watermark_opacity is not None: wm_params_edit['opacity'] = config.default_watermark_opacity

                    if request.watermark_scale is not None: wm_params_edit['scale'] = request.watermark_scale
                    if request.watermark_padding is not None: wm_params_edit['padding'] = request.watermark_padding

                    watermarked_bytes = apply_watermark(
                        img_bytes_to_watermark,
                        current_watermark_path_to_use_for_edit,
                        target_format=request.output_format, # Use format from request
                        **wm_params_edit
                    )
                    saved_path_obj.write_bytes(watermarked_bytes)
                    print(f"✅ Watermark applied to {saved_path_obj.name}")
                except FileNotFoundError: # Should be caught by apply_watermark, but good to be safe
                    print(f"⚠️ Watermark image file not found at '{current_watermark_path_to_use_for_edit}' for {saved_path_obj.name}. Skipping.")
                except Exception as wm_e_edit:
                    print(f"⚠️ Error applying watermark to {saved_path_obj.name}: {wm_e_edit}. Skipping for this image.")
        # --- End Watermarking Step for edit_or_vary_image ---

        if not processed_output_paths:
            return "❌ No images were successfully generated or saved."
        return f"✅ Images generated: {', '.join(processed_output_paths)}"

    except openai.APIError as e:
        return f"❌ OpenAI API Error: {str(e)}"
    except ValueError as e:
        return f"❌ Validation Error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected Error in edit_or_vary_image: {str(e)}"
    finally:
        if temp_watermark_path_for_request and temp_watermark_path_for_request.exists():
            try:
                temp_watermark_path_for_request.unlink()
            except Exception as e_clean:
                print(f"⚠️ Warning: Failed to clean up temporary watermark for edit: {e_clean}")


if __name__ == "__main__":
    main()