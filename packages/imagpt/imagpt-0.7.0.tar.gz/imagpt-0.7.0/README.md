# imagpt 🎨

A powerful CLI tool with persistent configuration and MCP server support for generating images using OpenAI's API. Generate images from text prompts directly, process entire directories of prompt files, or integrate with LLMs through the Model Context Protocol.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI API](https://img.shields.io/badge/OpenAI-API-green.svg)](https://openai.com/api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🔧 **Persistent Configuration**: Save API keys, default models, and preferences
- 🚀 **Direct Prompt Generation**: Generate images from command-line prompts
- 📁 **Batch Processing**: Process entire directories of prompt files
- 🤖 **MCP Server**: Model Context Protocol server for LLM integration
- 🖼️ **Image Processing**: Built-in rescaling and cropping capabilities
- 🎯 **Multiple Formats**: Support for `.prompt`, `.txt`, and `.md` files
- 🔄 **Smart Skipping**: Skip existing images to save time and API costs
- ⚡ **Rate Limiting**: Configurable delays to respect API limits
- 🎨 **Multi-Model Support**: gpt-image-1, DALL-E 3, and DALL-E 2
- 🌈 **Rich CLI**: Beautiful colored output with Typer and Rich
- 📦 **Easy Install**: Install globally with pipx

## 🚀 Quick Start

### Install with pipx (Recommended)

```bash
pipx install imagpt
```

### Install with pip

```bash
pip install imagpt
```

### Set up your API key

```bash
# Option 1: Save in configuration (recommended)
imagpt config set openai_api_key "your-api-key-here"

# Option 2: Use environment variable
export OPENAI_API_KEY="your-api-key-here"
```

### Generate your first image

```bash
imagpt generate "A majestic dragon flying over a medieval castle at sunset"
```

### Start the MCP server for LLM integration

```bash
# For local MCP clients (like Claude Desktop)
imagpt mcp-server

# Or run without installing
pipx run imagpt mcp-server
```

## 🤖 MCP Server

imagpt includes a **Model Context Protocol (MCP) server** that allows LLMs to generate images through standardized MCP tools. This enables AI assistants to create images directly through the MCP protocol.

### Available MCP Tools

- **`generate_single_image`**: Generate a single image from a text prompt with rescaling and cropping
- **`generate_batch_images`**: Generate images from all prompt files in a directory with processing options
- **`edit_or_vary_image`**: Edit an existing image using a prompt or create variations. Accepts base64 encoded image data, an optional prompt, and optional base64 mask data. Returns paths to generated temporary image files.
- **`list_prompt_files`**: List available prompt files in a directory
- **`show_config`**: Display current imagpt configuration
- **`update_config`**: Update configuration settings

### Running the MCP Server

#### After Installation (Recommended)

```bash
# Install once with pipx
pipx install imagpt

# Then run the MCP server
imagpt mcp-server

# With different transports
imagpt mcp-server --transport streamable-http --port 8000
imagpt mcp-server --transport sse --port 8000

# Custom configuration
imagpt mcp-server --transport streamable-http --host 0.0.0.0 --port 9000 --path /api/mcp
```

#### One-time Usage with pipx run

```bash
# Run without installing (useful for testing)
pipx run imagpt mcp-server

# With options
pipx run imagpt mcp-server --transport streamable-http --port 8000

# Specify version
pipx run imagpt==0.4.0 mcp-server
```

#### Development Usage

```bash
# In development environment
poetry run imagpt mcp-server

# Or with pip install -e
pip install -e .
imagpt mcp-server

# Or test with pipx run from local directory
pipx run --spec . imagpt mcp-server
```

### MCP Client Configuration

#### For STDIO Transport (Recommended for local use)

**After installing with pipx:**
```json
{
  "mcpServers": {
    "imagpt": {
      "command": "imagpt",
      "args": ["mcp-server"]
    }
  }
}
```

**Using pipx run (no installation required):**
```json
{
  "mcpServers": {
    "imagpt": {
      "command": "pipx",
      "args": ["run", "imagpt", "mcp-server"]
    }
  }
}
```

**With specific version using pipx run:**
```json
{
  "mcpServers": {
    "imagpt": {
      "command": "pipx",
      "args": ["run", "imagpt==0.4.0", "mcp-server"]
    }
  }
}
```

#### For HTTP Transport (Web deployments)

Start the server first:
```bash
# With pipx install
imagpt mcp-server --transport streamable-http --port 8000

# Or with pipx run
pipx run imagpt mcp-server --transport streamable-http --port 8000
```

Then configure your client:
```json
{
  "mcpServers": {
    "imagpt": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

#### Development Setup

If you're developing locally with poetry:

```json
{
  "mcpServers": {
    "imagpt": {
      "command": "poetry",
      "args": ["run", "imagpt", "mcp-server"],
      "cwd": "/path/to/imagpt"
    }
  }
}
```

## 📖 Usage

### Configuration Management

Set up your preferences once and use them everywhere:

```bash
# Set up your API key and preferences
imagpt config set openai_api_key "your-key-here"
imagpt config set default_model "dall-e-3"
imagpt config set default_quality "hd"
imagpt config set default_output_dir "~/Pictures/AI-Generated"

# View current configuration
imagpt config show

# Reset to defaults
imagpt config reset
```

### Direct Prompt Generation

Generate a single image from a text prompt:

```bash
# Basic usage (uses your configured defaults)
imagpt generate "A cute robot playing guitar"

# Override defaults for specific generation
imagpt generate "A space station orbiting Earth" --output space_station.png --model gpt-image-1

# Custom output location
imagpt generate "Abstract art with vibrant colors" --output ./art/abstract.png
```

### Batch Processing from Directory

Process multiple prompt files at once:

```bash
# Process all prompt files in a directory (uses configured defaults)
imagpt generate --dir ./my_prompts

# Save to different output directory
imagpt generate --dir ./prompts --output ./generated_images

# Skip existing images and use faster processing
imagpt generate --dir ./prompts --skip-existing --delay 1
```

### Image Editing and Variations: `imagpt edit`

The `edit` command allows you to modify an existing image based on a text prompt or create variations of it.

-   **Editing**: Provide an image and a prompt to describe the desired changes. You can also use a mask for more precise control over the edited area.
-   **Variations**: If no prompt is supplied, the command will generate variations of the input image.

**Options:**

*   `image_path`: (Required) Path to the source image file (e.g., `.png`, `.jpg`).
*   `--prompt <text>` / `-p <text>`: (Optional) A text description of the desired edit. If omitted, the command generates variations of the image.
*   `--mask <mask_path>` / `-m <mask_path>`: (Optional) Path to a PNG mask file. Transparent areas in the mask indicate where the image should be edited by the prompt.
*   `--output <output_path>` / `-o <output_path>`: (Optional) Specify the output file name or path. If not set, the output is saved in the current directory or a configured default directory, with a name derived from the input image (e.g., `input_edit.png` or `input_variation_0.png`).
*   `--n <number>`: (Optional) Number of images to generate. Defaults to 1. For DALL-E 2, this can be 1-10. For `gpt-image-1` edits, it must be 1.
*   `--model <model_name>`: (Optional) Specify the model to use (`dall-e-2` or `gpt-image-1`). The tool defaults to `dall-e-2` for edits and variations. `gpt-image-1` can be used for edits if specified.
*   `--size <WxH>`: (Optional) The dimensions of the generated images (e.g., `1024x1024`, `512x512`). Must be one of the sizes supported by the chosen model.
*   `--quality <quality_level>`: (Optional) For `gpt-image-1` edits, specifies quality (`low`, `medium`, `high`). Defaults to `auto`. Not applicable to `dall-e-2` which uses `standard` quality implicitly.
*   `--background <bg_type>`: (Optional) For `gpt-image-1` edits, defines background handling (`transparent`, `opaque`, `auto`).
*   `--response-format <format>`: (Optional) For `dall-e-2`, specifies response format (`url` or `b64_json`). `gpt-image-1` always uses `b64_json`. Defaults to `b64_json`.

**Examples:**

1.  **Editing an image with a prompt:**
    ```bash
    imagpt edit path/to/your/image.png --prompt "Make it a cyberpunk style" -o path/to/output/cyberpunk_image.png
    ```

2.  **Creating variations of an image:**
    ```bash
    imagpt edit path/to/your/otter.png --n 2 -o path/to/output/otter_variation.png
    ```
    This will create `otter_variation_0.png` and `otter_variation_1.png` in the specified output path. If `-o` pointed to a directory, files would be named similarly within that directory.

3.  **Editing with a mask for precise changes:**
    ```bash
    imagpt edit path/to/original.png --prompt "Add sunglasses to the person" --mask path/to/face_mask.png -o path/to/output/sunglasses_edit.png
    ```

## 📁 Supported File Formats

### `.prompt` files
```
A beautiful sunset over snow-capped mountains with a lake reflection
```

### `.txt` files
```
A futuristic cityscape with flying cars and neon lights
```

### `.md` files (with special parsing)
```markdown
# Image Description

**Description:**
A serene Japanese garden with cherry blossoms, a small bridge over a koi pond, and traditional lanterns. The scene should be peaceful and zen-like.

**Style:** Photorealistic
**Mood:** Tranquil
```

## 🖼️ Image Processing

imagpt includes built-in image processing capabilities to rescale and crop generated images:

### Rescaling
- **`--rescale SIZE`**: Resize the generated image to the specified dimensions
- Format: `WIDTHxHEIGHT` (e.g., `512x512`, `800x600`)
- Uses high-quality Lanczos resampling for best results
- Useful for creating thumbnails or reducing file sizes

### Cropping
- **`--crop-left PIXELS`**: Remove pixels from the left edge
- **`--crop-right PIXELS`**: Remove pixels from the right edge  
- **`--crop-top PIXELS`**: Remove pixels from the top edge
- **`--crop-bottom PIXELS`**: Remove pixels from the bottom edge
- Useful for removing unwanted borders or focusing on specific areas

### Processing Order
When both cropping and rescaling are specified, cropping is applied first, then rescaling. This allows you to crop to the desired composition and then resize to the target dimensions.

### Examples
```bash
# Create a 512x512 thumbnail
imagpt generate "A beautiful sunset" --rescale 512x512

# Remove 50px border from all sides
imagpt generate "A framed artwork" --crop-left 50 --crop-right 50 --crop-top 50 --crop-bottom 50

# Crop to remove top/bottom letterboxing, then resize
imagpt generate "A wide panorama" --crop-top 100 --crop-bottom 100 --rescale 1200x600

# Set defaults for consistent processing
imagpt config set default_rescale "800x800"
imagpt config set default_crop_top 20
imagpt config set default_crop_bottom 20
```

## 🛠️ Command Line Options

### Main Commands

```bash
imagpt generate [OPTIONS] [PROMPT]    # Generate images
imagpt config [COMMAND]               # Manage configuration  
imagpt mcp-server [OPTIONS]           # Start MCP server for LLM integration
imagpt version                         # Show version
```

### Generate Command Options

```
Arguments:
  PROMPT                    Direct prompt text for image generation

Options:
  --dir PATH               Directory containing prompt files
  --output PATH            Output file/directory path
  --delay FLOAT            Delay between API calls in seconds
  --skip-existing          Skip generating images that already exist
  --model MODEL            Model to use: gpt-image-1, dall-e-2, dall-e-3
  --size SIZE              Image dimensions (e.g., 1024x1024, 1536x1024, 1024x1536)
  --quality QUALITY        Image quality: auto, high, medium, low, hd, standard
  --style STYLE            Image style for DALL-E 3: vivid, natural
  --format FORMAT          Output format: png, jpeg, webp
  --rescale SIZE           Rescale image to size (e.g., 512x512, 800x600)
  --crop-left PIXELS       Crop pixels from left edge
  --crop-right PIXELS      Crop pixels from right edge
  --crop-top PIXELS        Crop pixels from top edge
  --crop-bottom PIXELS     Crop pixels from bottom edge
  --help                   Show help message and exit
```

### Configuration Commands

```bash
imagpt config show                    # Display current configuration
imagpt config set KEY VALUE           # Set a configuration value
imagpt config reset                   # Reset to default configuration
imagpt config path                    # Show configuration file path
```

## 📋 Examples

### Configuration Examples

```bash
# First-time setup
imagpt config set openai_api_key "your-key-here"
imagpt config set default_model "dall-e-3"
imagpt config set default_quality "hd"
imagpt config set default_output_dir "~/Pictures/AI-Generated"

# View your settings
imagpt config show

# Update specific settings
imagpt config set default_size "1792x1024"
imagpt config set skip_existing true
```

### Single Image Generation

```bash
# Simple prompt (uses your configured defaults)
imagpt generate "A red sports car"

# Complex prompt with details
imagpt generate "A detailed oil painting of a lighthouse on a rocky cliff during a storm, dramatic lighting, high contrast"

# Save with custom name
imagpt generate "A minimalist logo design" --output company_logo.png

# Override defaults for specific generation
imagpt generate "A futuristic cityscape" --model dall-e-3 --size 1792x1024 --style vivid

# Generate portrait orientation
imagpt generate "A portrait of a wise old wizard" --size 1024x1536

# Use DALL-E 2 for faster generation
imagpt generate "A simple cartoon cat" --model dall-e-2 --size 512x512

# Generate JPEG format
imagpt generate "A landscape photo" --format jpeg --quality high

# Generate and rescale to smaller size
imagpt generate "A detailed artwork" --rescale 512x512

# Generate and crop edges
imagpt generate "A portrait photo" --crop-left 50 --crop-right 50 --crop-top 20 --crop-bottom 20

# Generate, crop, and rescale (crop first, then rescale)
imagpt generate "A wide landscape" --crop-top 100 --crop-bottom 100 --rescale 800x400
```

### Batch Processing

```bash
# Process directory (saves images alongside prompts)
imagpt generate --dir ./product_descriptions

# Separate input/output directories
imagpt generate --dir ./marketing_prompts --output ./marketing_images

# Production settings (skip existing, faster processing)
imagpt generate --dir ./prompts --output ./images --skip-existing --delay 0.5

# Batch process with DALL-E 3 for high quality
imagpt generate --dir ./art_prompts --model dall-e-3 --quality hd --style natural

# Generate thumbnails with DALL-E 2
imagpt generate --dir ./thumbnails --model dall-e-2 --size 256x256

# Batch process with custom format and quality
imagpt generate --dir ./web_images --format webp --quality medium --delay 1

# Batch process with rescaling for thumbnails
imagpt generate --dir ./prompts --output ./thumbnails --rescale 256x256

# Batch process with cropping and rescaling
imagpt generate --dir ./wide_images --crop-top 50 --crop-bottom 50 --rescale 800x600
```

## 🔧 Configuration

### Configuration File

imagpt stores configuration in a platform-specific location:
- **macOS**: `~/Library/Application Support/imagpt/config.toml`
- **Linux**: `~/.config/imagpt/config.toml`  
- **Windows**: `%APPDATA%/imagpt/config.toml`

### Configuration Options

| Setting | Type | Description | Default |
|---------|------|-------------|---------|
| `openai_api_key` | string | Your OpenAI API key | None |
| `default_model` | string | Default model (gpt-image-1, dall-e-2, dall-e-3) | gpt-image-1 |
| `default_size` | string | Default image size (e.g., 1024x1024) | Auto |
| `default_quality` | string | Default quality (auto, high, medium, low, hd, standard) | high |
| `default_style` | string | Default style for DALL-E 3 (vivid, natural) | None |
| `default_format` | string | Default output format (png, jpeg, webp) | png |
| `default_rescale` | string | Default rescale size (e.g., 512x512) | None |
| `default_crop_left` | integer | Default left crop in pixels | None |
| `default_crop_right` | integer | Default right crop in pixels | None |
| `default_crop_top` | integer | Default top crop in pixels | None |
| `default_crop_bottom` | integer | Default bottom crop in pixels | None |
| `default_prompts_dir` | string | Default directory for prompt files | None |
| `default_output_dir` | string | Default directory for generated images | None |
| `default_delay` | float | Default delay between API calls (seconds) | 2.0 |
| `skip_existing` | boolean | Default setting for skipping existing images | false |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | Your OpenAI API key (fallback if not in config) |

### Image Settings

The tool supports multiple models and configurations:

#### Models
- **gpt-image-1** (default): OpenAI's latest image model
  - Sizes: 1024x1024, 1536x1024 (landscape), 1024x1536 (portrait)
  - Quality: auto, high, medium, low
  - Formats: png, jpeg, webp
- **dall-e-3**: High-quality artistic images
  - Sizes: 1024x1024, 1792x1024 (landscape), 1024x1792 (portrait)
  - Quality: auto, hd, standard
  - Styles: vivid, natural
- **dall-e-2**: Fast and cost-effective
  - Sizes: 256x256, 512x512, 1024x1024
  - Quality: standard only

## 📦 Installation Methods

### Method 1: pipx (Recommended)

```bash
# Install globally without affecting system Python
pipx install imagpt

# Upgrade
pipx upgrade imagpt

# Uninstall
pipx uninstall imagpt
```

### Method 2: pip

```bash
# Install globally
pip install imagpt

# Install in virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install imagpt
```

### Method 3: Development Install

For developers who want to contribute or modify the code, see the [DEVELOPERS.md](DEVELOPERS.md) guide for detailed setup instructions.

## 🚨 Error Handling

The tool gracefully handles various error conditions:

- **Missing API Key**: Clear instructions for setting up authentication
- **Empty Prompts**: Skips empty files with warnings
- **API Errors**: Continues processing other files if one fails
- **Network Issues**: Retries with exponential backoff
- **Invalid Paths**: Validates input/output directories

## 💡 Tips & Best Practices

### Writing Better Prompts

1. **Be Specific**: Include details about style, lighting, composition
2. **Use Descriptive Language**: "vibrant", "detailed", "photorealistic"
3. **Specify Art Style**: "oil painting", "digital art", "photograph"
4. **Include Mood**: "serene", "dramatic", "whimsical"

### Batch Processing

1. **Organize Prompts**: Use descriptive filenames for easy identification
2. **Use Skip Existing**: Avoid regenerating images unnecessarily
3. **Adjust Delays**: Balance speed vs. API rate limits
4. **Separate Outputs**: Keep generated images organized

### Cost Management

1. **Preview Prompts**: Review prompts before batch processing
2. **Use Skip Existing**: Avoid duplicate generations
3. **Test Single Images**: Verify prompts work before batch runs
4. **Monitor Usage**: Track API usage in OpenAI dashboard

## 🤝 Contributing

Contributions are welcome! Please see [DEVELOPERS.md](DEVELOPERS.md) for detailed development setup, testing, and contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 **Email**: jacobfv123@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/humanrobots-ai/imagpt/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/humanrobots-ai/imagpt/discussions)

## 🙏 Acknowledgments

- OpenAI for providing the amazing image generation API
- The Python community for excellent tooling and libraries
- All contributors and users of this tool

---

Made with ❤️ by [Jacob Valdez](https://github.com/jacobfv123) 