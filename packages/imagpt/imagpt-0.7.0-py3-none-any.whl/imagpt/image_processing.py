#!/usr/bin/env python3
"""
Image processing utilities for imagpt.

Handles post-generation image processing like rescaling and cropping.
"""

from pathlib import Path
from typing import Optional, Tuple
import io

from PIL import Image
from rich import print as rprint


def parse_size(size_str: str) -> Tuple[int, int]:
    """Parse size string like '800x600' into (width, height) tuple."""
    try:
        parts = size_str.split('x')
        if len(parts) != 2:
            raise ValueError("Size must be in format 'WIDTHxHEIGHT'")
        
        width, height = int(parts[0]), int(parts[1])
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")
        
        return width, height
    except ValueError as e:
        raise ValueError(f"Invalid size format '{size_str}': {e}")


def rescale_image(image_data: bytes, target_size: str, output_format: str = "png") -> bytes:
    """
    Rescale an image to the target size.
    
    Args:
        image_data: Original image data as bytes
        target_size: Target size in format 'WIDTHxHEIGHT' (e.g., '512x512')
        output_format: Output format ('png', 'jpeg', 'webp')
    
    Returns:
        Rescaled image data as bytes
    """
    try:
        # Parse target size
        target_width, target_height = parse_size(target_size)
        
        # Open image from bytes
        image = Image.open(io.BytesIO(image_data))
        original_size = image.size
        
        rprint(f"🔄 Rescaling image from {original_size[0]}x{original_size[1]} to {target_width}x{target_height}")
        
        # Rescale image using high-quality resampling
        rescaled_image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Convert to bytes
        output_buffer = io.BytesIO()
        
        # Handle format-specific options
        save_kwargs = {}
        if output_format.lower() == 'jpeg':
            save_kwargs['quality'] = 95
            save_kwargs['optimize'] = True
            # Convert RGBA to RGB for JPEG
            if rescaled_image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', rescaled_image.size, (255, 255, 255))
                background.paste(rescaled_image, mask=rescaled_image.split()[-1] if rescaled_image.mode == 'RGBA' else None)
                rescaled_image = background
        elif output_format.lower() == 'webp':
            save_kwargs['quality'] = 95
            save_kwargs['optimize'] = True
        elif output_format.lower() == 'png':
            save_kwargs['optimize'] = True
        
        rescaled_image.save(output_buffer, format=output_format.upper(), **save_kwargs)
        
        rprint(f"✅ Image rescaled successfully")
        return output_buffer.getvalue()
        
    except Exception as e:
        rprint(f"❌ Error rescaling image: {e}")
        raise


def crop_image(
    image_data: bytes, 
    left: Optional[int] = None,
    top: Optional[int] = None,
    right: Optional[int] = None,
    bottom: Optional[int] = None,
    output_format: str = "png"
) -> bytes:
    """
    Crop an image by removing pixels from the specified edges.
    
    Args:
        image_data: Original image data as bytes
        left: Pixels to crop from left edge
        top: Pixels to crop from top edge
        right: Pixels to crop from right edge
        bottom: Pixels to crop from bottom edge
        output_format: Output format ('png', 'jpeg', 'webp')
    
    Returns:
        Cropped image data as bytes
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_data))
        original_width, original_height = image.size
        
        # Calculate crop box
        crop_left = left or 0
        crop_top = top or 0
        crop_right = original_width - (right or 0)
        crop_bottom = original_height - (bottom or 0)
        
        # Validate crop parameters
        if crop_left >= crop_right or crop_top >= crop_bottom:
            raise ValueError("Invalid crop parameters: would result in zero or negative dimensions")
        
        if crop_left < 0 or crop_top < 0 or crop_right > original_width or crop_bottom > original_height:
            raise ValueError("Crop parameters exceed image dimensions")
        
        crop_info = []
        if left: crop_info.append(f"left: {left}px")
        if top: crop_info.append(f"top: {top}px")
        if right: crop_info.append(f"right: {right}px")
        if bottom: crop_info.append(f"bottom: {bottom}px")
        
        if crop_info:
            rprint(f"✂️  Cropping image ({', '.join(crop_info)})")
            rprint(f"   Original: {original_width}x{original_height} → Cropped: {crop_right - crop_left}x{crop_bottom - crop_top}")
            
            # Crop the image
            cropped_image = image.crop((crop_left, crop_top, crop_right, crop_bottom))
            
            # Convert to bytes
            output_buffer = io.BytesIO()
            
            # Handle format-specific options
            save_kwargs = {}
            if output_format.lower() == 'jpeg':
                save_kwargs['quality'] = 95
                save_kwargs['optimize'] = True
                # Convert RGBA to RGB for JPEG
                if cropped_image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', cropped_image.size, (255, 255, 255))
                    background.paste(cropped_image, mask=cropped_image.split()[-1] if cropped_image.mode == 'RGBA' else None)
                    cropped_image = background
            elif output_format.lower() == 'webp':
                save_kwargs['quality'] = 95
                save_kwargs['optimize'] = True
            elif output_format.lower() == 'png':
                save_kwargs['optimize'] = True
            
            cropped_image.save(output_buffer, format=output_format.upper(), **save_kwargs)
            
            rprint(f"✅ Image cropped successfully")
            return output_buffer.getvalue()
        else:
            # No cropping needed, return original
            return image_data
            
    except Exception as e:
        rprint(f"❌ Error cropping image: {e}")
        raise


def process_image(
    image_data: bytes,
    rescale: Optional[str] = None,
    crop_left: Optional[int] = None,
    crop_top: Optional[int] = None,
    crop_right: Optional[int] = None,
    crop_bottom: Optional[int] = None,
    output_format: str = "png"
) -> bytes:
    """
    Process an image with optional rescaling and cropping.
    
    Processing order: crop first, then rescale.
    
    Args:
        image_data: Original image data as bytes
        rescale: Target size for rescaling in format 'WIDTHxHEIGHT'
        crop_left: Pixels to crop from left edge
        crop_top: Pixels to crop from top edge
        crop_right: Pixels to crop from right edge
        crop_bottom: Pixels to crop from bottom edge
        output_format: Output format ('png', 'jpeg', 'webp')
    
    Returns:
        Processed image data as bytes
    """
    processed_data = image_data
    
    # Apply cropping first (if any crop parameters are specified)
    if any([crop_left, crop_top, crop_right, crop_bottom]):
        processed_data = crop_image(
            processed_data, crop_left, crop_top, crop_right, crop_bottom, output_format
        )
    
    # Apply rescaling (if specified)
    if rescale:
        processed_data = rescale_image(processed_data, rescale, output_format)
    
    return processed_data


from PIL import ImageEnhance # Added ImageEnhance

def apply_watermark(
    base_image_bytes: bytes,
    watermark_image_path: str,
    position: str = "bottomright", 
    opacity: float = 0.5,
    scale: float = 0.1, 
    padding: int = 10,
    target_format: str = "PNG" 
) -> bytes:
    """
    Apply a watermark to a base image. Returns bytes in the specified target_format.
    """
    try:
        base_img = Image.open(io.BytesIO(base_image_bytes)).convert("RGBA")
        watermark_img_original = Image.open(watermark_image_path).convert("RGBA")
    except FileNotFoundError:
        rprint(f"❌ Watermark image not found at: {watermark_image_path}")
        raise 
    except Exception as e:
        rprint(f"❌ Error opening images for watermarking: {e}")
        raise

    # Create a copy to avoid modifying the original watermark image object if it's cached
    watermark_img = watermark_img_original.copy()

    # Adjust Watermark Opacity
    if opacity < 1.0:
        if watermark_img.mode != 'RGBA':
             watermark_img = watermark_img.convert('RGBA') # Should already be RGBA from initial load
        
        alpha = watermark_img.split()[3]
        # Per instructions, use ImageEnhance.Brightness for opacity
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        watermark_img.putalpha(alpha)

    # Scale Watermark
    wm_target_size = int(min(base_img.width, base_img.height) * scale)
    watermark_img.thumbnail((wm_target_size, wm_target_size), Image.Resampling.LANCZOS)

    # Determine Position
    pos_x, pos_y = 0, 0
    if position == "topleft":
        pos_x, pos_y = padding, padding
    elif position == "topright":
        pos_x, pos_y = base_img.width - watermark_img.width - padding, padding
    elif position == "bottomleft":
        pos_x, pos_y = padding, base_img.height - watermark_img.height - padding
    elif position == "bottomright":
        pos_x, pos_y = base_img.width - watermark_img.width - padding, base_img.height - watermark_img.height - padding
    elif position == "center":
        pos_x, pos_y = (base_img.width - watermark_img.width) // 2, (base_img.height - watermark_img.height) // 2
    else: 
        rprint(f"⚠️ Invalid watermark position '{position}'. Defaulting to 'bottomright'.")
        pos_x, pos_y = base_img.width - watermark_img.width - padding, base_img.height - watermark_img.height - padding
        
    # Composite Images
    transparent_layer = Image.new('RGBA', base_img.size, (0,0,0,0))
    transparent_layer.paste(watermark_img, (pos_x, pos_y), watermark_img) 
    
    composited_img = Image.alpha_composite(base_img, transparent_layer)

    # Return Bytes (in target_format)
    img_byte_arr = io.BytesIO()
    save_kwargs = {}
    final_save_img = composited_img # Default to composited_img, which is RGBA
    
    # Prepare image for saving in the target format
    if target_format.upper() == 'JPEG':
        save_kwargs['quality'] = 95 
        save_kwargs['optimize'] = True
        # For JPEG, need to convert to RGB. Create white background if original had alpha.
        if composited_img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', composited_img.size, (255, 255, 255))
            # Paste using the alpha channel of the composited image as the mask
            background.paste(composited_img, mask=composited_img.split()[-1]) 
            final_save_img = background
        elif composited_img.mode != 'RGB': # If it's P, L etc. but not RGBA/LA
             final_save_img = composited_img.convert('RGB')
        # If already RGB, final_save_img remains composited_img (which is already RGB after conversion)

    elif target_format.upper() == 'WEBP':
        save_kwargs['quality'] = 95 
        # WebP supports RGBA, so final_save_img can remain composited_img (which is RGBA)
        # If lossless is desired and image is RGBA, Pillow handles it.
        # save_kwargs['lossless'] = True # Optionally
    elif target_format.upper() == 'PNG':
        save_kwargs['optimize'] = True
        # PNG supports RGBA, so final_save_img can remain composited_img

    final_save_img.save(img_byte_arr, format=target_format.upper(), **save_kwargs)
    final_image_bytes = img_byte_arr.getvalue()
    
    return final_image_bytes