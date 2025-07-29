#!/usr/bin/env python3
"""
Image Generator from Prompt Files or Direct Prompts

This script generates images from text prompt files or direct prompt input using OpenAI's API.
Can be used as a CLI tool or installed via pipx.

Usage:
    # From directory of prompt files
    imagpt generate --dir <prompts_dir> [--output <output_dir>]

    # From direct prompt
    imagpt generate "A beautiful sunset over mountains"

    # Save to specific file
    imagpt generate "A robot in space" --output robot_space.png

    # Configuration management
    imagpt config show
    imagpt config set openai_api_key "your-key-here"
    imagpt config set default_model "dall-e-3"
"""

import os
import sys
import base64
import time
from pathlib import Path
from typing import List, Optional, Annotated

import openai
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .config import config_manager, ImageptConfig
from .image_processing import process_image, apply_watermark

# Initialize Typer app and console
app = typer.Typer(
    name="imagpt",
    help="🎨 AI Image Generator - Generate images using OpenAI API from prompt files, direct input, or through LLM integration via MCP server.",
    rich_markup_mode="rich",
)
config_app = typer.Typer(help="🔧 Configuration management")
app.add_typer(config_app, name="config")

library_app = typer.Typer(
    name="library",
    help="📚 Manage your prompt library. Saved prompts can include default generation parameters and watermarking settings."
)
app.add_typer(library_app, name="library")

console = Console()


def read_prompt_file(prompt_path: Path) -> str:
    """Read prompt content from a file."""
    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # If it's a markdown file, try to extract description
    if prompt_path.suffix.lower() == ".md":
        lines = content.split("\n")
        description_lines = []
        in_description = False

        for line in lines:
            if line.startswith("**Description:**"):
                in_description = True
                continue
            elif in_description and line.startswith("**"):
                break
            elif in_description and line.strip():
                description_lines.append(line.strip())

        # If description found, use it; otherwise use cleaned content
        if description_lines:
            return " ".join(description_lines)
        else:
            # Remove markdown headers and formatting for a cleaner prompt
            clean_lines = []
            for line in lines:
                if (
                    not line.startswith("#")
                    and not line.startswith("**")
                    and line.strip()
                ):
                    clean_lines.append(line.strip())
            return " ".join(clean_lines)

    return content


def generate_image(
    client: openai.OpenAI,
    prompt: str,
    filename: str,
    model: str = "gpt-image-1",
    size: str = "1536x1024",
    quality: str = "high",
    style: str = None,
    output_format: str = "png",
) -> bytes:
    """Generate an image using OpenAI's API."""
    rprint(f"🎨 Generating image for [bold]{filename}[/bold]...")
    rprint(f"📝 Prompt: [dim]{prompt[:100]}{'...' if len(prompt) > 100 else ''}[/dim]")
    rprint(
        f"🔧 Model: [cyan]{model}[/cyan], Size: [cyan]{size}[/cyan], Quality: [cyan]{quality}[/cyan]"
    )

    try:
        # Validate and truncate prompt based on model
        max_lengths = {"gpt-image-1": 32000, "dall-e-2": 1000, "dall-e-3": 4000}

        max_length = max_lengths.get(model, 32000)
        if len(prompt) > max_length:
            prompt = prompt[:max_length] + "..."
            rprint(
                f"⚠️  Warning: Prompt truncated to {max_length} characters for {model}"
            )

        # Build API parameters based on model
        api_params = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": quality,
        }

        # Add model-specific parameters
        if model == "gpt-image-1":
            if output_format in ["png", "jpeg", "webp"]:
                api_params["output_format"] = output_format
        elif model == "dall-e-3":
            if style in ["vivid", "natural"]:
                api_params["style"] = style
            # dall-e-3 uses response_format instead of output_format
            api_params["response_format"] = "b64_json"
        elif model == "dall-e-2":
            # dall-e-2 uses response_format
            api_params["response_format"] = "b64_json"

        # Generate image
        response = client.images.generate(**api_params)

        # Decode base64 image data
        image_data = base64.b64decode(response.data[0].b64_json)

        rprint(
            f"✅ Successfully generated image for [bold green]{filename}[/bold green]"
        )
        return image_data

    except Exception as e:
        rprint(f"❌ Error generating image for {filename}: {str(e)}")
        raise


def save_image(
    image_data: bytes, 
    output_path: Path,
    rescale: Optional[str] = None,
    crop_left: Optional[int] = None,
    crop_right: Optional[int] = None,
    crop_top: Optional[int] = None,
    crop_bottom: Optional[int] = None,
    output_format: str = "png",
    watermark_path: Optional[str] = None,
    watermark_position: Optional[str] = None,
    watermark_opacity: Optional[float] = None,
    watermark_scale: Optional[float] = None,
    watermark_padding: Optional[int] = None
):
    """Save image data to file with optional watermarking and processing."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    current_image_data = image_data # Data to be processed

    if watermark_path: # Check if watermark_path is provided
        try:
            wm_params = {} # Collect non-None watermark parameters
            if watermark_position is not None: wm_params['position'] = watermark_position
            if watermark_opacity is not None: wm_params['opacity'] = watermark_opacity
            if watermark_scale is not None: wm_params['scale'] = watermark_scale
            if watermark_padding is not None: wm_params['padding'] = watermark_padding
            
            rprint(f"💧 Applying watermark from [bold cyan]{watermark_path}[/bold cyan]...")
            current_image_data = apply_watermark(
                base_image_bytes=current_image_data,
                watermark_image_path=watermark_path,
                **wm_params # Pass other params if they are not None
            )
        except FileNotFoundError: # Specific error from apply_watermark if file not found
            rprint(f"⚠️ Watermark image not found at [bold red]{watermark_path}[/bold red]. Skipping watermark.")
        except Exception as e: # Catch other errors from apply_watermark or Pillow
            rprint(f"⚠️ Error applying watermark: {e}. Skipping watermark.")

    # Existing image processing (rescale, crop)
    # This should now operate on 'current_image_data'
    if rescale or any([crop_left, crop_right, crop_top, crop_bottom]):
        processed_data = process_image(
            current_image_data, rescale, crop_left, crop_top, crop_right, crop_bottom, output_format
        )
    else:
        processed_data = current_image_data

    with open(output_path, "wb") as f:
        f.write(processed_data)

    rprint(f"💾 Saved image to [bold blue]{output_path}[/bold blue]")


def find_prompt_files(prompts_dir: Path) -> List[Path]:
    """Find all prompt files in the directory."""
    prompt_files = []

    # Look for various prompt file extensions
    extensions = [".prompt", ".txt", ".md"]

    for ext in extensions:
        prompt_files.extend(prompts_dir.glob(f"*{ext}"))

    return sorted(prompt_files)


def get_output_path(
    prompt_file: Path, output_dir: Path, output_format: str = "png"
) -> Path:
    """Get the output path for a prompt file."""
    # Remove the prompt extension and add the output format extension
    base_name = prompt_file.stem
    return output_dir / f"{base_name}.{output_format}"


def validate_model_size(model: str, size: str) -> bool:
    """Validate that the size is compatible with the model."""
    valid_sizes = {
        "gpt-image-1": ["1024x1024", "1536x1024", "1024x1536"],
        "dall-e-2": ["256x256", "512x512", "1024x1024"],
        "dall-e-3": ["1024x1024", "1792x1024", "1024x1792"],
    }

    return size in valid_sizes.get(model, [])


def get_default_size(model: str) -> str:
    """Get default size for a model."""
    size_defaults = {
        "gpt-image-1": "1536x1024",
        "dall-e-2": "1024x1024",
        "dall-e-3": "1024x1024",
    }
    return size_defaults.get(model, "1536x1024")


@app.command()
def generate(
    prompt: Annotated[
        Optional[str], typer.Argument(help="Direct prompt text for image generation. Optional if using --from-library or --dir.")
    ] = None,
    dir: Annotated[
        Optional[str], typer.Option("--dir", help="Directory containing prompt files")
    ] = None,
    from_library_name: Annotated[
        Optional[str], typer.Option("--from-library", help="Generate using a prompt from the library.")
    ] = None,
    output: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            help="Output file path (for direct prompts) or directory (for prompt files)",
        ),
    ] = None,
    model: Annotated[
        Optional[str], typer.Option("--model", help="Model to use for image generation")
    ] = None,
    size: Annotated[
        Optional[str],
        typer.Option(
            "--size", help="Image size (e.g., 1024x1024, 1536x1024, 1024x1536)"
        ),
    ] = None,
    quality: Annotated[
        Optional[str], typer.Option("--quality", help="Image quality")
    ] = None,
    style: Annotated[
        Optional[str],
        typer.Option("--style", help="Image style for DALL-E 3 (vivid or natural)"),
    ] = None,
    format: Annotated[
        Optional[str], typer.Option("--format", help="Output format")
    ] = None,
    rescale: Annotated[
        Optional[str],
        typer.Option("--rescale", help="Rescale image to size (e.g., 512x512, 800x600)"),
    ] = None,
    crop_left: Annotated[
        Optional[int],
        typer.Option("--crop-left", help="Crop pixels from left edge"),
    ] = None,
    crop_right: Annotated[
        Optional[int],
        typer.Option("--crop-right", help="Crop pixels from right edge"),
    ] = None,
    crop_top: Annotated[
        Optional[int],
        typer.Option("--crop-top", help="Crop pixels from top edge"),
    ] = None,
    crop_bottom: Annotated[
        Optional[int],
        typer.Option("--crop-bottom", help="Crop pixels from bottom edge"),
    ] = None,
    delay: Annotated[
        Optional[float],
        typer.Option("--delay", help="Delay between API calls in seconds"),
    ] = None,
    skip_existing: Annotated[
        bool,
        typer.Option(
            "--skip-existing", help="Skip generating images that already exist"
        ),
    ] = False,
    # Watermark options for CLI override
    watermark_image: Annotated[Optional[Path], typer.Option("--watermark-image", help="Path to watermark image.")] = None,
    watermark_position: Annotated[Optional[str], typer.Option("--watermark-position", help="Watermark position (e.g., bottomright).")] = None,
    watermark_opacity: Annotated[Optional[float], typer.Option("--watermark-opacity", help="Watermark opacity (0.0-1.0).")] = None,
    watermark_scale: Annotated[Optional[float], typer.Option("--watermark-scale", help="Watermark scale relative to image size.")] = None,
    watermark_padding: Annotated[Optional[int], typer.Option("--watermark-padding", help="Watermark padding in pixels.")] = None,
):
    """🎨 Generate images from prompts or prompt files."""

    config = config_manager.load_config()
    lib_prompt_data = None

    if from_library_name:
        lib_prompt_data = config_manager.get_prompt_from_library(from_library_name)
        if not lib_prompt_data:
            rprint(f"❌ Error: Library prompt '{from_library_name}' not found.")
            raise typer.Exit(1)
        current_prompt_text = prompt or lib_prompt_data.get("text")
    else:
        current_prompt_text = prompt

    if not current_prompt_text and not dir:
        rprint("❌ Error: Must provide a prompt, use --from-library, or specify a directory with --dir.")
        raise typer.Exit(1)

    # Parameter precedence: CLI > Library > Config Default
    effective_model = model # CLI model
    if effective_model is None and lib_prompt_data: effective_model = lib_prompt_data.get("model")
    if effective_model is None: effective_model = config.default_model

    effective_size = size # CLI size
    if effective_size is None and lib_prompt_data: effective_size = lib_prompt_data.get("size")
    if effective_size is None: effective_size = config.default_size or get_default_size(effective_model) # get_default_size needs a model

    effective_quality = quality # CLI quality
    if effective_quality is None and lib_prompt_data: effective_quality = lib_prompt_data.get("quality")
    if effective_quality is None: effective_quality = config.default_quality
    
    effective_style = style # CLI style
    if effective_style is None and lib_prompt_data: effective_style = lib_prompt_data.get("style")
    if effective_style is None: effective_style = config.default_style

    effective_format = format # CLI format
    if effective_format is None and lib_prompt_data: effective_format = lib_prompt_data.get("format")
    if effective_format is None: effective_format = config.default_format

    effective_rescale = rescale # CLI rescale
    if effective_rescale is None and lib_prompt_data: effective_rescale = lib_prompt_data.get("rescale")
    if effective_rescale is None: effective_rescale = config.default_rescale
    
    effective_crop_left = crop_left
    if effective_crop_left is None and lib_prompt_data: effective_crop_left = lib_prompt_data.get("crop_left")
    if effective_crop_left is None: effective_crop_left = config.default_crop_left

    effective_crop_right = crop_right
    if effective_crop_right is None and lib_prompt_data: effective_crop_right = lib_prompt_data.get("crop_right")
    if effective_crop_right is None: effective_crop_right = config.default_crop_right

    effective_crop_top = crop_top
    if effective_crop_top is None and lib_prompt_data: effective_crop_top = lib_prompt_data.get("crop_top")
    if effective_crop_top is None: effective_crop_top = config.default_crop_top

    effective_crop_bottom = crop_bottom
    if effective_crop_bottom is None and lib_prompt_data: effective_crop_bottom = lib_prompt_data.get("crop_bottom")
    if effective_crop_bottom is None: effective_crop_bottom = config.default_crop_bottom

    # Watermark parameters precedence
    effective_wm_path = str(watermark_image) if watermark_image else None
    if effective_wm_path is None and lib_prompt_data: effective_wm_path = lib_prompt_data.get("watermark_image_path")
    if effective_wm_path is None: effective_wm_path = config.default_watermark_image_path

    effective_wm_pos = watermark_position
    if effective_wm_pos is None and lib_prompt_data: effective_wm_pos = lib_prompt_data.get("watermark_position")
    if effective_wm_pos is None: effective_wm_pos = config.default_watermark_position

    effective_wm_opacity = watermark_opacity
    if effective_wm_opacity is None and lib_prompt_data: effective_wm_opacity = lib_prompt_data.get("watermark_opacity")
    if effective_wm_opacity is None: effective_wm_opacity = config.default_watermark_opacity

    effective_wm_scale = watermark_scale
    if effective_wm_scale is None and lib_prompt_data: effective_wm_scale = lib_prompt_data.get("watermark_scale")
    if effective_wm_scale is None: # No default scale in config, this might be fine or use a hardcoded default if necessary for apply_watermark
        pass 

    effective_wm_padding = watermark_padding
    if effective_wm_padding is None and lib_prompt_data: effective_wm_padding = lib_prompt_data.get("watermark_padding")
    if effective_wm_padding is None: # No default padding in config
        pass


    # Validate inputs (after resolving parameters)
    if not current_prompt_text and not dir: # Re-check, though earlier check should catch this
        rprint("❌ Error: Must provide a prompt, use --from-library, or specify a directory with --dir.")
        raise typer.Exit(1)

    if current_prompt_text and dir: # This check is fine
        rprint("❌ Error: Cannot use both direct prompt/--from-library and directory mode (--dir)")
        raise typer.Exit(1)

    if not validate_model_size(effective_model, effective_size):
        valid_sizes = {
            "gpt-image-1": ["1024x1024", "1536x1024", "1024x1536"],
            "dall-e-2": ["256x256", "512x512", "1024x1024"],
            "dall-e-3": ["1024x1024", "1792x1024", "1024x1792"],
        }
        rprint(f"❌ Error: Size '{effective_size}' is not valid for model '{effective_model}'")
        rprint(f"Valid sizes for {effective_model}: {', '.join(valid_sizes.get(effective_model, ['N/A']))}")
        raise typer.Exit(1)

    rprint("🤖 [bold]AI Image Generator[/bold]")
    rprint("=" * 50)

    # Initialize OpenAI client
    try:
        api_key = config_manager.get_api_key()
        client = openai.OpenAI(api_key=api_key)
        rprint("✅ OpenAI client initialized")
    except Exception as e:
        rprint(f"❌ Failed to initialize OpenAI client: {e}")
        raise typer.Exit(1)

    # Handle directory mode
    if dir:
        prompts_dir = Path(dir)
        effective_output_dir = ( # Renamed output to effective_output_dir to avoid conflict
            Path(output)
            if output
            else (
                Path(config.default_output_dir)
                if config.default_output_dir
                else prompts_dir
            )
        )

        if not prompts_dir.exists():
            rprint(f"❌ Prompts directory does not exist: {prompts_dir}")
            raise typer.Exit(1)

        if not prompts_dir.is_dir():
            rprint(f"❌ Prompts path is not a directory: {prompts_dir}")
            raise typer.Exit(1)

        rprint(f"📁 Prompts directory: [bold blue]{prompts_dir}[/bold blue]")
        rprint(f"📂 Output directory: [bold blue]{effective_output_dir}[/bold blue]")

        prompt_files = find_prompt_files(prompts_dir)
        if not prompt_files:
            rprint(f"❌ No prompt files found in {prompts_dir}")
            rprint("Looking for files with extensions: .prompt, .txt, .md")
            raise typer.Exit(1)

        rprint(f"📁 Found [bold]{len(prompt_files)}[/bold] prompt files")
        success_count = 0
        for prompt_file_path in prompt_files: # Renamed prompt_file to prompt_file_path
            try:
                current_output_path = get_output_path(prompt_file_path, effective_output_dir, effective_format)

                if skip_existing and current_output_path.exists():
                    rprint(f"⏭️  Skipping [dim]{prompt_file_path.name}[/dim] (image already exists)")
                    continue

                file_prompt_text = read_prompt_file(prompt_file_path)
                if not file_prompt_text.strip():
                    rprint(f"⚠️  Skipping [dim]{prompt_file_path.name}[/dim] (empty prompt)")
                    continue

                image_data = generate_image(
                    client, file_prompt_text, prompt_file_path.name,
                    effective_model, effective_size, effective_quality, effective_style, effective_format
                )
                save_image(
                    image_data, current_output_path, 
                    effective_rescale, effective_crop_left, effective_crop_right, 
                    effective_crop_top, effective_crop_bottom, effective_format,
                    effective_wm_path, effective_wm_pos, effective_wm_opacity,
                    effective_wm_scale, effective_wm_padding
                )
                success_count += 1
                if delay > 0: time.sleep(delay)
            except Exception as e:
                rprint(f"❌ Failed to process {prompt_file_path.name}: {e}")
                continue
        rprint(f"\n🎉 [bold green]Image generation complete![/bold green]")
        rprint(f"✅ Successfully generated [bold]{success_count}/{len(prompt_files)}[/bold] images")
        rprint(f"📂 Images saved to: [bold blue]{effective_output_dir}[/bold blue]")

    # Handle direct prompt mode (or --from-library)
    else:
        final_output_path = None
        if output:
            final_output_path = Path(output)
            if final_output_path.suffix.lower() != f".{effective_format}":
                final_output_path = final_output_path.with_suffix(f".{effective_format}")
        else:
            output_base_dir = Path(config.default_output_dir) if config.default_output_dir else Path.cwd()
            safe_name_base = from_library_name or current_prompt_text[:30]
            safe_name = "".join(c for c in safe_name_base if c.isalnum() or c in (" ", "-", "_")).rstrip()
            safe_name = safe_name.replace(" ", "_").lower()
            final_output_path = output_base_dir / f"{safe_name}.{effective_format}"

        rprint(f"📝 Prompt: [dim]{current_prompt_text}[/dim]")
        rprint(f"📂 Output: [bold blue]{final_output_path}[/bold blue]")

        try:
            image_data = generate_image(
                client, current_prompt_text, final_output_path.name, 
                effective_model, effective_size, effective_quality, effective_style, effective_format
            )
            save_image(
                image_data, final_output_path, 
                effective_rescale, effective_crop_left, effective_crop_right, 
                effective_crop_top, effective_crop_bottom, effective_format,
                effective_wm_path, effective_wm_pos, effective_wm_opacity,
                effective_wm_scale, effective_wm_padding
            )
            rprint(f"\n🎉 [bold green]Image generation complete![/bold green]")
            rprint(f"📂 Image saved to: [bold blue]{final_output_path}[/bold blue]")
        except Exception as e:
            rprint(f"❌ Failed to generate image: {e}")
            raise typer.Exit(1)


@app.command()
def edit(
    image_path: Annotated[Path, typer.Argument(help="Path to the source image file.")],
    prompt: Annotated[Optional[str], typer.Option("--prompt", "-p", help="A text description of the desired edit. If not provided, or if using --from-library without a new prompt, creates a variation or uses library prompt.")] = None,
    mask_path: Annotated[Optional[Path], typer.Option("--mask", "-m", help="Path to an optional mask image (PNG) for edits.")] = None,
    output_path: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file path.")] = None,
    n: Annotated[int, typer.Option("--n", help="Number of images to generate (1-10).")] = 1,
    model: Annotated[Optional[str], typer.Option("--model", help="Model: 'dall-e-2', 'gpt-image-1'.")] = None,
    size: Annotated[Optional[str], typer.Option("--size", help="Image size.")] = None,
    quality: Annotated[Optional[str], typer.Option("--quality", help="Quality (gpt-image-1: low, medium, high; dall-e-2: standard).")] = None,
    background: Annotated[Optional[str], typer.Option("--background", help="Background for gpt-image-1 (transparent, opaque, auto).")] = None,
    response_format: Annotated[Optional[str], typer.Option("--response-format", help="API response format (url or b64_json).")] = None,
    from_library_name: Annotated[Optional[str], typer.Option("--from-library", help="Use prompt text and settings from the library for editing.")] = None,
    # Watermark options for CLI override
    watermark_image: Annotated[Optional[Path], typer.Option("--watermark-image", help="Path to watermark image.")] = None,
    watermark_position: Annotated[Optional[str], typer.Option("--watermark-position", help="Watermark position.")] = None,
    watermark_opacity: Annotated[Optional[float], typer.Option("--watermark-opacity", help="Watermark opacity (0.0-1.0).")] = None,
    watermark_scale: Annotated[Optional[float], typer.Option("--watermark-scale", help="Watermark scale.")] = None,
    watermark_padding: Annotated[Optional[int], typer.Option("--watermark-padding", help="Watermark padding.")] = None,
):
    """🖌️ Edit an image or create variations, optionally using library settings."""

    config = config_manager.load_config()
    lib_prompt_data = None

    if from_library_name:
        lib_prompt_data = config_manager.get_prompt_from_library(from_library_name)
        if not lib_prompt_data:
            rprint(f"❌ Error: Library prompt '{from_library_name}' not found.")
            raise typer.Exit(1)

    current_prompt_text = prompt # Direct CLI prompt
    if current_prompt_text is None and lib_prompt_data:
        current_prompt_text = lib_prompt_data.get("text")
    # If current_prompt_text is still None, it's a variation

    # Parameter precedence for API call parameters
    effective_model_api = model # CLI
    if effective_model_api is None and lib_prompt_data: effective_model_api = lib_prompt_data.get("model")
    # If still None, logic within edit/variation part will set default (e.g. dall-e-2)

    effective_size_api = size # CLI
    if effective_size_api is None and lib_prompt_data: effective_size_api = lib_prompt_data.get("size")
    # If still None, logic within edit/variation part will set default based on model

    effective_quality_api = quality # CLI
    if effective_quality_api is None and lib_prompt_data: effective_quality_api = lib_prompt_data.get("quality")
    # If still None, logic within edit/variation part will set default

    # Parameter precedence for watermark settings (passed to save_image)
    effective_wm_path = str(watermark_image) if watermark_image else None
    if effective_wm_path is None and lib_prompt_data: effective_wm_path = lib_prompt_data.get("watermark_image_path")
    if effective_wm_path is None: effective_wm_path = config.default_watermark_image_path
    
    effective_wm_pos = watermark_position
    if effective_wm_pos is None and lib_prompt_data: effective_wm_pos = lib_prompt_data.get("watermark_position")
    if effective_wm_pos is None: effective_wm_pos = config.default_watermark_position

    effective_wm_opacity = watermark_opacity
    if effective_wm_opacity is None and lib_prompt_data: effective_wm_opacity = lib_prompt_data.get("watermark_opacity")
    if effective_wm_opacity is None: effective_wm_opacity = config.default_watermark_opacity

    effective_wm_scale = watermark_scale
    if effective_wm_scale is None and lib_prompt_data: effective_wm_scale = lib_prompt_data.get("watermark_scale")
    # No config default for scale, apply_watermark has its own default

    effective_wm_padding = watermark_padding
    if effective_wm_padding is None and lib_prompt_data: effective_wm_padding = lib_prompt_data.get("watermark_padding")
    # No config default for padding, apply_watermark has its own default
    
    # Determine output format from config, as edit doesn't have a direct format option
    # but save_image needs it for watermarking and final save.
    # This could also come from lib_prompt_data if "format" is stored there.
    effective_output_format = (lib_prompt_data.get("format") if lib_prompt_data else None) or config.default_format or "png"


    try:
        api_key = config_manager.get_api_key()
        client = openai.OpenAI(api_key=api_key)
        rprint("✅ OpenAI client initialized")
    except Exception as e:
        rprint(f"❌ Failed to initialize OpenAI client: {e}")
        raise typer.Exit(1)

    if not image_path.exists():
        rprint(f"❌ Source image not found: {image_path}")
        raise typer.Exit(1)

    opened_image_file = open(image_path, "rb") # Renamed to avoid conflict
    opened_mask_file = None # Renamed
    if mask_path:
        if not mask_path.exists():
            rprint(f"❌ Mask image not found: {mask_path}")
            if opened_image_file: opened_image_file.close()
            raise typer.Exit(1)
        opened_mask_file = open(mask_path, "rb")

    if not (1 <= n <= 10):
        rprint("❌ Error: Number of images (n) must be between 1 and 10.")
        if opened_image_file: opened_image_file.close()
        if opened_mask_file: opened_mask_file.close()
        raise typer.Exit(1)
        
    # Use effective_model_api for this check as it's the one passed to API
    if effective_model_api == "gpt-image-1" and n > 1 and current_prompt_text:
        rprint("⚠️ Warning: gpt-image-1 edits support n=1 only. Setting n=1.")
        n = 1

    try:
        final_api_model = effective_model_api
        final_api_size = effective_size_api
        final_api_quality = effective_quality_api

        if current_prompt_text:  # Image Edit
            rprint(f"🎨 Editing image [bold]{image_path.name}[/bold] with prompt...")
            if final_api_model is None: final_api_model = "dall-e-2" # Default for edit if not set by CLI/Lib
            if final_api_size is None: final_api_size = get_default_size(final_api_model)
            if final_api_quality is None and final_api_model == "gpt-image-1": final_api_quality = "auto"


            if final_api_model == "dall-e-2":
                if quality and quality != "standard": rprint(f"⚠️ Warning: Model 'dall-e-2' only supports 'standard' quality. Ignoring quality='{quality}'.")
                # DALL-E 2 quality is implicit (standard)
                final_api_quality_param = None 
                final_api_response_format = response_format or "b64_json"
                if background: rprint(f"⚠️ Warning: Background parameter is only for 'gpt-image-1'. Ignoring background='{background}'.")
                valid_sizes = ["256x256", "512x512", "1024x1024"]
                if final_api_size not in valid_sizes:
                    rprint(f"❌ Error: Size '{final_api_size}' is not valid for model 'dall-e-2'. Valid sizes: {', '.join(valid_sizes)}")
                    raise typer.Exit(1)
            elif final_api_model == "gpt-image-1":
                if final_api_quality == "standard": final_api_quality = "auto" # Alias
                final_api_quality_param = final_api_quality
                if response_format and response_format != "b64_json": rprint(f"⚠️ Warning: Model 'gpt-image-1' always uses b64_json. Ignoring.")
                final_api_response_format = "b64_json"
                valid_sizes = ["1024x1024", "1536x1024", "1024x1536"] # Check docs
                if final_api_size not in valid_sizes:
                    rprint(f"❌ Error: Size '{final_api_size}' is not valid for 'gpt-image-1' edits. Valid sizes: {', '.join(valid_sizes)}")
                    raise typer.Exit(1)
                if n > 1: # Already handled, but as safeguard
                    rprint("⚠️ Warning: gpt-image-1 edits only support n=1. Setting n=1.")
                    n = 1
            else:
                rprint(f"❌ Error: Unsupported model for edit: {final_api_model}")
                raise typer.Exit(1)

            api_params = {"image": opened_image_file, "prompt": current_prompt_text, "model": final_api_model, "n": n, "size": final_api_size}
            if opened_mask_file: api_params["mask"] = opened_mask_file
            if final_api_model == "gpt-image-1":
                if final_api_quality_param and final_api_quality_param != "auto": api_params["quality"] = final_api_quality_param
                if background: api_params["background"] = background
            elif final_api_model == "dall-e-2":
                api_params["response_format"] = final_api_response_format
            
            rprint(f"🔧 Using model: [cyan]{final_api_model}[/cyan], Size: [cyan]{final_api_size}[/cyan]")
            response = client.images.edit(**api_params)
        else:  # Image Variation
            rprint(f"🧬 Creating variation for image [bold]{image_path.name}[/bold]...")
            final_api_model = "dall-e-2" # Variations API only supports dall-e-2
            if model and model != "dall-e-2": rprint(f"⚠️ Warning: Variations only support 'dall-e-2'. Ignoring model='{model}'.")
            if final_api_size is None: final_api_size = get_default_size(final_api_model) # Usually 1024x1024 for DALL-E 2
            
            if quality and quality != "standard": rprint(f"⚠️ Warning: DALL-E 2 variations use 'standard' quality. Ignoring quality='{quality}'.")
            if background: rprint(f"⚠️ Warning: Background parameter is only for 'gpt-image-1'. Ignoring background='{background}'.")
            final_api_response_format = response_format or "b64_json"
            valid_sizes = ["256x256", "512x512", "1024x1024"]
            if final_api_size not in valid_sizes:
                rprint(f"❌ Error: Size '{final_api_size}' is not valid for 'dall-e-2' variations. Valid sizes: {', '.join(valid_sizes)}")
                raise typer.Exit(1)

            api_params = {"image": opened_image_file, "model": final_api_model, "n": n, "size": final_api_size, "response_format": final_api_response_format}
            rprint(f"🔧 Using model: [cyan]{final_api_model}[/cyan], Size: [cyan]{final_api_size}[/cyan]")
            response = client.images.create_variation(**api_params)

        generated_image_data_list = []
        for i, image_object in enumerate(response.data):
            img_data = None
            if hasattr(image_object, "url") and image_object.url:
                if final_api_response_format == "url":
                    rprint(f"🔗 Image URL ({i+1}/{n}): {image_object.url}")
                    try:
                        import httpx
                        http_resp = httpx.get(image_object.url)
                        http_resp.raise_for_status()
                        img_data = http_resp.content
                        rprint(f"✅ Downloaded image data from URL ({i+1}/{n})")
                    except Exception as e:
                        rprint(f"❌ Failed to download image from URL ({image_object.url}): {e}")
                        continue
                elif hasattr(image_object, "b64_json") and image_object.b64_json:
                    img_data = base64.b64decode(image_object.b64_json)
                else:
                    rprint(f"⚠️ Image object {i+1} has URL but no b64_json, and response_format was not 'url'. Skipping.")
                    continue
            elif hasattr(image_object, "b64_json") and image_object.b64_json:
                img_data = base64.b64decode(image_object.b64_json)
            
            if not img_data:
                rprint(f"❌ No image data found for image {i+1}. Skipping.")
                continue
            generated_image_data_list.append(img_data)

        for i, single_image_data in enumerate(generated_image_data_list):
            current_output_path = None
            if output_path:
                if n > 1: current_output_path = output_path.parent / f"{output_path.stem}_{i}{output_path.suffix}"
                else: current_output_path = output_path
            else:
                base_dir = Path(config.default_output_dir) if config.default_output_dir else Path.cwd()
                op_suffix = "_edit" if current_prompt_text else "_variation"
                idx_suffix = f"_{i}" if n > 1 else ""
                current_output_path = base_dir / f"{image_path.stem}{op_suffix}{idx_suffix}.{effective_output_format}"
            
            current_output_path.parent.mkdir(parents=True, exist_ok=True)
            save_image(
                single_image_data, current_output_path, 
                output_format=effective_output_format, # Pass the determined output format
                watermark_path=effective_wm_path, 
                watermark_position=effective_wm_pos,
                watermark_opacity=effective_wm_opacity,
                watermark_scale=effective_wm_scale,
                watermark_padding=effective_wm_padding
            )
        rprint(f"\n🎉 [bold green]Image {'editing' if current_prompt_text else 'variation'} complete![/bold green]")

    except openai.APIError as e:
        rprint(f"❌ OpenAI API Error: {e}")
        if "Invalid size" in str(e) and final_api_model == "gpt-image-1":
             rprint("ℹ️ For gpt-image-1 edits, ensure your image is square and one of the supported resolutions if not using DALL-E 2.")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"❌ An unexpected error occurred: {e}")
        raise typer.Exit(1)
    finally:
        if opened_image_file: opened_image_file.close()
        if opened_mask_file: opened_mask_file.close()


@config_app.command("show")
def config_show():
    """📋 Show current configuration."""
    config_manager.show_config()


@config_app.command("set")
def config_set(
    key: Annotated[str, typer.Argument(help="Configuration key to set")],
    value: Annotated[str, typer.Argument(help="Configuration value to set")],
):
    """⚙️ Set a configuration value."""
    try:
        # Convert string values to appropriate types
        if key in ["default_delay"]:
            value = float(value)
        elif key in ["skip_existing"]:
            value = value.lower() in ["true", "1", "yes", "on"]
        elif key in ["default_crop_left", "default_crop_right", "default_crop_top", "default_crop_bottom"]:
            value = int(value) if value.lower() != "none" else None

        config_manager.update_config(**{key: value})
        rprint(f"✅ Set [bold]{key}[/bold] = [cyan]{value}[/cyan]")
    except Exception as e:
        rprint(f"❌ Failed to set configuration: {e}")
        raise typer.Exit(1)


@config_app.command("reset")
def config_reset():
    """🔄 Reset configuration to defaults."""
    if typer.confirm("Are you sure you want to reset all configuration to defaults?"):
        config_manager.reset_config()
        rprint("✅ Configuration reset to defaults")
    else:
        rprint("❌ Configuration reset cancelled")


@config_app.command("path")
def config_path():
    """📁 Show configuration file path."""
    rprint(
        f"📄 Configuration file: [bold blue]{config_manager.config_file}[/bold blue]"
    )


@app.command()
def mcp_server(
    transport: Annotated[
        str,
        typer.Option(
            "--transport", help="Transport protocol (stdio, streamable-http, sse)"
        ),
    ] = "stdio",
    host: Annotated[
        str, typer.Option("--host", help="Host to bind to (for HTTP transports)")
    ] = "127.0.0.1",
    port: Annotated[
        int, typer.Option("--port", help="Port to bind to (for HTTP transports)")
    ] = 8000,
    path: Annotated[
        str, typer.Option("--path", help="Path for MCP endpoint (for HTTP transports)")
    ] = "/mcp",
    log_level: Annotated[
        str, typer.Option("--log-level", help="Log level (debug, info, warning, error)")
    ] = "info",
):
    """🤖 Start the MCP (Model Context Protocol) server for imagpt."""
    try:
        from .mcp_server import mcp

        rprint("🤖 [bold]Starting imagpt MCP Server[/bold]")
        rprint(f"🚀 Transport: [cyan]{transport}[/cyan]")

        if transport == "stdio":
            rprint("📡 Listening on STDIO for MCP client connections...")
            mcp.run(transport="stdio")
        elif transport == "streamable-http":
            rprint(
                f"🌐 Starting HTTP server on [cyan]http://{host}:{port}{path}[/cyan]"
            )
            mcp.run(
                transport="streamable-http",
                host=host,
                port=port,
                path=path,
                log_level=log_level,
            )
        elif transport == "sse":
            rprint(f"🌐 Starting SSE server on [cyan]http://{host}:{port}{path}[/cyan]")
            rprint(
                "⚠️  [yellow]Note: SSE transport is deprecated, consider using streamable-http[/yellow]"
            )
            mcp.run(
                transport="sse", host=host, port=port, path=path, log_level=log_level
            )
        else:
            rprint(f"❌ Unknown transport: {transport}")
            rprint("Available transports: stdio, streamable-http, sse")
            raise typer.Exit(1)

    except ImportError:
        rprint("❌ FastMCP not available. Install with: pip install fastmcp")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"❌ Failed to start MCP server: {e}")
        raise typer.Exit(1)


@app.command()
def version():
    """📋 Show version information."""
    rprint("🎨 [bold]imagpt[/bold] v0.7.0") # This should be updated by a future step if version changes
    rprint("AI Image Generator with persistent configuration and MCP server support")
    rprint("Made with ❤️  by Jacob Valdez")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()


# --- Library Commands ---

@library_app.command("add")
def library_add(
    name: Annotated[str, typer.Argument(help="Unique name for this library prompt.")],
    prompt_text: Annotated[str, typer.Argument(help="The text of the prompt.")],
    model: Annotated[Optional[str], typer.Option("--model", help="Default model for this prompt.")] = None,
    size: Annotated[Optional[str], typer.Option("--size", help="Default size for this prompt.")] = None,
    quality: Annotated[Optional[str], typer.Option("--quality", help="Default quality for this prompt.")] = None,
    style: Annotated[Optional[str], typer.Option("--style", help="Default style for this prompt.")] = None,
    lib_watermark_image: Annotated[Optional[Path], typer.Option("--watermark-image", help="Path to watermark image for this prompt.")] = None,
    lib_watermark_position: Annotated[Optional[str], typer.Option("--watermark-position", help="Watermark position (e.g., bottomright).")] = None,
    lib_watermark_opacity: Annotated[Optional[float], typer.Option("--watermark-opacity", help="Watermark opacity (0.0-1.0).")] = None,
    lib_watermark_scale: Annotated[Optional[float], typer.Option("--watermark-scale", help="Watermark scale relative to image size.")] = None,
    lib_watermark_padding: Annotated[Optional[int], typer.Option("--watermark-padding", help="Watermark padding in pixels.")] = None,
    # Added for completeness, matching config options
    fmt: Annotated[Optional[str], typer.Option("--format", help="Default output format for this prompt (png, jpeg, webp).")] = None, # renamed to fmt to avoid conflict
    rescale: Annotated[Optional[str], typer.Option("--rescale", help="Default rescale size (e.g., 512x512).")] = None,
    crop_left: Annotated[Optional[int], typer.Option("--crop-left", help="Default crop pixels from left.")] = None,
    crop_right: Annotated[Optional[int], typer.Option("--crop-right", help="Default crop pixels from right.")] = None,
    crop_top: Annotated[Optional[int], typer.Option("--crop-top", help="Default crop pixels from top.")] = None,
    crop_bottom: Annotated[Optional[int], typer.Option("--crop-bottom", help="Default crop pixels from bottom.")] = None,
):
    """💾 Add a new prompt with its settings to the library."""
    if not name.strip():
        rprint("❌ Error: Prompt name cannot be empty.")
        raise typer.Exit(1)
        
    prompt_attributes = {"text": prompt_text}
    if model: prompt_attributes["model"] = model
    if size: prompt_attributes["size"] = size
    if quality: prompt_attributes["quality"] = quality
    if style: prompt_attributes["style"] = style
    if lib_watermark_image: prompt_attributes["watermark_image_path"] = str(lib_watermark_image)
    if lib_watermark_position: prompt_attributes["watermark_position"] = lib_watermark_position
    if lib_watermark_opacity is not None: prompt_attributes["watermark_opacity"] = lib_watermark_opacity
    if lib_watermark_scale is not None: prompt_attributes["watermark_scale"] = lib_watermark_scale
    if lib_watermark_padding is not None: prompt_attributes["watermark_padding"] = lib_watermark_padding
    if fmt: prompt_attributes["format"] = fmt
    if rescale: prompt_attributes["rescale"] = rescale
    if crop_left is not None: prompt_attributes["crop_left"] = crop_left
    if crop_right is not None: prompt_attributes["crop_right"] = crop_right
    if crop_top is not None: prompt_attributes["crop_top"] = crop_top
    if crop_bottom is not None: prompt_attributes["crop_bottom"] = crop_bottom

    if config_manager.add_prompt_to_library(name, prompt_attributes):
        rprint(f"✅ Prompt '[bold green]{name}[/bold green]' added to library.")
    else:
        rprint(f"❌ Failed to add prompt '{name}' to library. Ensure prompt text is provided.")


@library_app.command("list")
def library_list():
    """📜 List all prompts currently in the library."""
    prompts = config_manager.list_library_prompts()
    if not prompts:
        rprint("📖 Prompt library is empty.")
        return

    table = Table(title="📚 Prompt Library")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Prompt Text", style="magenta")
    table.add_column("Model", style="green")
    table.add_column("Size", style="yellow")
    table.add_column("Watermark", style="blue")

    for name, attrs in prompts.items():
        text_preview = attrs.get("text", "")[:70] + "..." if len(attrs.get("text", "")) > 70 else attrs.get("text", "")
        wm_preview = "Yes" if attrs.get("watermark_image_path") else "No"
        table.add_row(name, text_preview, attrs.get("model", "-"), attrs.get("size", "-"), wm_preview)
    
    console.print(table)


@library_app.command("show")
def library_show(name: Annotated[str, typer.Argument(help="Name of the prompt to show.")]):
    """🔍 Show detailed information for a specific library prompt."""
    prompt_data = config_manager.get_prompt_from_library(name)
    if not prompt_data:
        rprint(f"❌ Error: Prompt '[bold red]{name}[/bold red]' not found in library.")
        raise typer.Exit(1)

    rprint(f"Detailed information for prompt: [bold cyan]{name}[/bold cyan]")
    for key, value in prompt_data.items():
        rprint(f"  [green]{key.replace('_', ' ').title()}[/green]: {value}")


@library_app.command("remove")
def library_remove(name: Annotated[str, typer.Argument(help="Name of the prompt to remove.")]):
    """🗑️ Remove a prompt from the library."""
    if config_manager.remove_prompt_from_library(name):
        rprint(f"✅ Prompt '[bold green]{name}[/bold green]' removed from library.")
    else:
        rprint(f"❌ Error: Prompt '[bold red]{name}[/bold red]' not found in library, or could not be removed.")


@library_app.command("update")
def library_update(
    name: Annotated[str, typer.Argument(help="Name of the library prompt to update.")],
    prompt_text: Annotated[Optional[str], typer.Option("--text", help="New prompt text.")] = None,
    model: Annotated[Optional[str], typer.Option("--model", help="New default model.")] = None,
    size: Annotated[Optional[str], typer.Option("--size", help="New default size.")] = None,
    quality: Annotated[Optional[str], typer.Option("--quality", help="New default quality.")] = None,
    style: Annotated[Optional[str], typer.Option("--style", help="New default style.")] = None,
    lib_watermark_image: Annotated[Optional[Path], typer.Option("--watermark-image", help="New path to watermark image. Use 'none' to remove.")] = None,
    lib_watermark_position: Annotated[Optional[str], typer.Option("--watermark-position", help="New watermark position.")] = None,
    lib_watermark_opacity: Annotated[Optional[float], typer.Option("--watermark-opacity", help="New watermark opacity.")] = None,
    lib_watermark_scale: Annotated[Optional[float], typer.Option("--watermark-scale", help="New watermark scale.")] = None,
    lib_watermark_padding: Annotated[Optional[int], typer.Option("--watermark-padding", help="New watermark padding.")] = None,
    fmt: Annotated[Optional[str], typer.Option("--format", help="New default output format.")] = None,
    rescale: Annotated[Optional[str], typer.Option("--rescale", help="New default rescale size.")] = None,
    crop_left: Annotated[Optional[int], typer.Option("--crop-left", help="New crop pixels from left.")] = None,
    crop_right: Annotated[Optional[int], typer.Option("--crop-right", help="New crop pixels from right.")] = None,
    crop_top: Annotated[Optional[int], typer.Option("--crop-top", help="New crop pixels from top.")] = None,
    crop_bottom: Annotated[Optional[int], typer.Option("--crop-bottom", help="New crop pixels from bottom.")] = None,
):
    """🔄 Update an existing prompt in the library. Only provided fields are changed."""
    existing_attrs = config_manager.get_prompt_from_library(name)
    if not existing_attrs:
        rprint(f"❌ Error: Prompt '[bold red]{name}[/bold red]' not found in library.")
        raise typer.Exit(1)

    updated_attrs = existing_attrs.copy() # Start with existing attributes

    if prompt_text is not None: updated_attrs["text"] = prompt_text
    if model is not None: updated_attrs["model"] = model
    if size is not None: updated_attrs["size"] = size
    if quality is not None: updated_attrs["quality"] = quality
    if style is not None: updated_attrs["style"] = style
    
    if lib_watermark_image is not None:
        if str(lib_watermark_image).lower() == 'none':
            updated_attrs["watermark_image_path"] = None
        else:
            updated_attrs["watermark_image_path"] = str(lib_watermark_image)
            
    if lib_watermark_position is not None: updated_attrs["watermark_position"] = lib_watermark_position
    if lib_watermark_opacity is not None: updated_attrs["watermark_opacity"] = lib_watermark_opacity
    if lib_watermark_scale is not None: updated_attrs["watermark_scale"] = lib_watermark_scale
    if lib_watermark_padding is not None: updated_attrs["watermark_padding"] = lib_watermark_padding
    
    if fmt is not None: updated_attrs["format"] = fmt
    if rescale is not None: updated_attrs["rescale"] = rescale
    if crop_left is not None: updated_attrs["crop_left"] = crop_left
    if crop_right is not None: updated_attrs["crop_right"] = crop_right
    if crop_top is not None: updated_attrs["crop_top"] = crop_top
    if crop_bottom is not None: updated_attrs["crop_bottom"] = crop_bottom
    
    # Filter out None values that might have been set by 'none' string for paths
    final_updated_attrs = {k: v for k, v in updated_attrs.items() if v is not None}


    if config_manager.add_prompt_to_library(name, final_updated_attrs):
        rprint(f"✅ Prompt '[bold green]{name}[/bold green]' updated successfully.")
    else:
        rprint(f"❌ Failed to update prompt '{name}'. Ensure prompt text is provided if it was cleared.")
