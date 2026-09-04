#!/usr/bin/env python3
"""
PPT Generator - Generate PPT slide images using Google Gemini API.

This script generates PPT slide images based on a slide plan and style template,
then creates an HTML viewer for playback.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv


# =============================================================================
# Constants
# =============================================================================

DEFAULT_RESOLUTION = "2K"

# --- Atlas Cloud（可选 provider）---------------------------------------------
# Gemini 官方 API 在部分地区不能直连。Atlas 走异步接口：提交任务 -> 轮询 ->
# 下载产物。默认模型选 seedream-v4，因为实测它精确遵守请求尺寸，能保住本项目
# 2K / 4K 的出图承诺（nano-banana 系列忽略 size，只认 aspect_ratio，出图约
# 1376x768，做 PPT 不够用）。
ATLAS_API_BASE = "https://api.atlascloud.ai/api/v1/model"
ATLAS_DEFAULT_MODEL = "bytedance/seedream-v4"
ATLAS_POLL_INTERVAL = 5
ATLAS_POLL_TIMEOUT = 600
# api.atlascloud.ai 会用 403(error code 1010) 拒掉部分客户端的默认 User-Agent
ATLAS_USER_AGENT = "nanobanana-ppt-skills/1"
# 本项目固定 16:9，这里直接给两档对应的像素尺寸（实测两档都精确返回）
ATLAS_SIZES = {"2K": "2048*1152", "4K": "3840*2160"}
DEFAULT_TEMPLATE_PATH = "templates/viewer.html"
OUTPUT_BASE_DIR = "outputs"

# Style template markers
TEMPLATE_START_MARKER = "## "
TEMPLATE_END_MARKER = "## "


# =============================================================================
# Environment Configuration
# =============================================================================

def find_and_load_env() -> bool:
    """
    Find and load .env file from multiple locations.

    Search priority:
    1. Current script directory
    2. Parent directories up to project root (containing .git or .env)
    3. Claude Code skill standard location (~/.claude/skills/ppt-generator/)

    Returns:
        True if .env file was found and loaded, False otherwise.
    """
    current_dir = Path(__file__).parent
    env_locations = [
        current_dir / ".env",
        *[parent / ".env" for parent in current_dir.parents],
        Path.home() / ".claude" / "skills" / "ppt-generator" / ".env",
    ]

    for env_path in env_locations:
        if env_path.exists():
            load_dotenv(env_path, override=True)
            print(f"Loaded environment from: {env_path}")
            return True

        # Stop at project root if .git exists
        if env_path.parent != current_dir and (env_path.parent / ".git").exists():
            break

    # Fallback: try default loading from system environment
    load_dotenv(override=True)
    print("Warning: No .env file found, using system environment variables")
    return False


# =============================================================================
# Style Template
# =============================================================================

def load_style_template(style_path: str) -> str:
    """
    Load and parse style template file.

    Args:
        style_path: Path to the style template markdown file.

    Returns:
        Extracted base prompt template string.
    """
    with open(style_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract base prompt template section
    start_marker = "## "
    end_marker = "## "

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx + len(start_marker))

    if start_idx == -1 or end_idx == -1:
        print("Warning: Could not parse style template, using full content")
        return content

    return content[start_idx + len(start_marker):end_idx].strip()


# =============================================================================
# Prompt Generation
# =============================================================================

def generate_prompt(
    style_template: str,
    page_type: str,
    content_text: str,
    slide_number: int,
    total_slides: int,
) -> str:
    """
    Generate a prompt for a single slide.

    Args:
        style_template: Base style template text.
        page_type: Type of page (cover, data, content).
        content_text: Text content for the slide.
        slide_number: Current slide number (1-indexed).
        total_slides: Total number of slides.

    Returns:
        Complete prompt string for image generation.
    """
    prompt_parts = [style_template, "\n\n"]

    # Determine page type based on slide position or explicit type
    is_cover = page_type == "cover" or slide_number == 1
    is_data = page_type == "data" or slide_number == total_slides

    if is_cover:
        prompt_parts.append(
            f"""Please generate a cover page based on visual balance aesthetics.
Place a large complex 3D glass object in the center, overlaid with bold text:

{content_text}

Background with extended aurora waves."""
        )
    elif is_data:
        prompt_parts.append(
            f"""Please generate a data/summary page using split-screen design.
Left side: typeset the following text.
Right side: floating large glowing 3D data visualization:

{content_text}"""
        )
    else:
        prompt_parts.append(
            f"""Please generate a content page using Bento grid layout.
Organize the following content in modular rounded rectangle containers.
Container material must be frosted glass with blur effect:

{content_text}"""
        )

    return "".join(prompt_parts)


# =============================================================================
# Image Generation
# =============================================================================

def get_gemini_client():
    """
    Initialize and return Gemini API client.

    Returns:
        Configured genai.Client instance.

    Raises:
        SystemExit: If google-genai is not installed or API key is missing.
    """
    try:
        from google import genai
    except ImportError:
        print("Error: google-genai library not installed")
        print("Please run: pip install google-genai")
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Please set: export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)

    return genai.Client(api_key=api_key)


def generate_slide_atlas(
    prompt: str,
    slide_number: int,
    output_dir: str,
    resolution: str = DEFAULT_RESOLUTION,
) -> Optional[str]:
    """
    Generate a single PPT slide image using Atlas Cloud.

    Atlas is an async API: submit a job, poll the prediction, download the
    result. Returns the same path/None contract as the Gemini path.
    """
    import time
    import urllib.error
    import urllib.request

    api_key = os.environ.get("ATLASCLOUD_API_KEY")
    if not api_key:
        print("Error: ATLASCLOUD_API_KEY environment variable not set")
        print("Please set: export ATLASCLOUD_API_KEY='your-api-key'")
        sys.exit(1)

    model = os.environ.get("ATLASCLOUD_IMAGE_MODEL") or ATLAS_DEFAULT_MODEL
    size = ATLAS_SIZES.get(resolution, ATLAS_SIZES[DEFAULT_RESOLUTION])

    def call(url: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {api_key}", "User-Agent": ATLAS_USER_AGENT}
        data = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url, data=data, headers=headers, method="POST" if payload is not None else "GET"
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))

    print(f"Generating slide {slide_number}...")

    try:
        submitted = call(
            f"{ATLAS_API_BASE}/generateImage",
            {"model": model, "prompt": prompt, "size": size},
        )
        prediction_id = (submitted.get("data") or {}).get("id")
        if not prediction_id:
            print(f"  Slide {slide_number} failed: no prediction id in response")
            return None

        deadline = time.monotonic() + ATLAS_POLL_TIMEOUT
        while True:
            time.sleep(ATLAS_POLL_INTERVAL)
            result = call(f"{ATLAS_API_BASE}/prediction/{prediction_id}")
            data = result.get("data") or {}
            status = data.get("status")
            if status == "completed":
                outputs = data.get("outputs") or []
                if not outputs:
                    print(f"  Slide {slide_number} failed: No image data received")
                    return None
                break
            if status == "failed":
                print(f"  Slide {slide_number} failed: {data.get('error') or status}")
                return None
            if time.monotonic() > deadline:
                print(f"  Slide {slide_number} failed: timed out after {ATLAS_POLL_TIMEOUT}s")
                return None

        download = urllib.request.Request(
            outputs[0], headers={"User-Agent": ATLAS_USER_AGENT}
        )
        with urllib.request.urlopen(download, timeout=300) as response:
            content = response.read()

        image_path = os.path.join(
            output_dir, "images", f"slide-{slide_number:02d}.png"
        )
        # The viewer HTML references images/slide-XX.png, and Atlas returns
        # whatever container the model produced (seedream-v4 returns JPEG), so
        # normalise to PNG instead of writing JPEG bytes under a .png name.
        if content[:8] == b"\x89PNG\r\n\x1a\n":
            with open(image_path, "wb") as handle:
                handle.write(content)
        else:
            try:
                from PIL import Image
            except ImportError:
                print("Error: pillow library not installed (needed to convert Atlas output to PNG)")
                print("Please run: pip install pillow")
                sys.exit(1)
            import io

            Image.open(io.BytesIO(content)).convert("RGB").save(image_path, format="PNG")

        print(f"  Slide {slide_number} saved: {image_path}")
        return image_path

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  Slide {slide_number} failed: HTTP {e.code} {body[:200]}")
        return None
    except Exception as e:
        print(f"  Slide {slide_number} failed: {e}")
        return None


def generate_slide(
    prompt: str,
    slide_number: int,
    output_dir: str,
    resolution: str = DEFAULT_RESOLUTION,
    provider: str = "gemini",
) -> Optional[str]:
    """
    Generate a single PPT slide image.

    Args:
        prompt: The generation prompt.
        slide_number: Slide number for filename.
        output_dir: Output directory path.
        resolution: Image resolution (2K or 4K).
        provider: "gemini" (default) or "atlas".

    Returns:
        Path to saved image, or None if generation failed.
    """
    if provider == "atlas":
        return generate_slide_atlas(prompt, slide_number, output_dir, resolution)

    from google.genai import types

    print(f"Generating slide {slide_number}...")

    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                    image_size=resolution,
                ),
            ),
        )

        for part in response.parts:
            if part.inline_data is not None:
                image = part.as_image()
                image_path = os.path.join(
                    output_dir, "images", f"slide-{slide_number:02d}.png"
                )
                image.save(image_path)
                print(f"  Slide {slide_number} saved: {image_path}")
                return image_path

        print(f"  Slide {slide_number} failed: No image data received")
        return None

    except Exception as e:
        print(f"  Slide {slide_number} failed: {e}")
        return None


# =============================================================================
# Output Generation
# =============================================================================

def generate_viewer_html(
    output_dir: str,
    slide_count: int,
    template_path: str,
) -> str:
    """
    Generate HTML viewer for slides playback.

    Args:
        output_dir: Output directory path.
        slide_count: Total number of slides.
        template_path: Path to HTML template.

    Returns:
        Path to generated HTML file.
    """
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    # Generate image list
    slides_list = [f"'images/slide-{i:02d}.png'" for i in range(1, slide_count + 1)]

    # Replace placeholder
    html_content = html_template.replace(
        "/* IMAGE_LIST_PLACEHOLDER */",
        ",\n            ".join(slides_list),
    )

    html_path = os.path.join(output_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"  Viewer HTML generated: {html_path}")
    return html_path


def save_prompts(output_dir: str, prompts_data: Dict[str, Any]) -> str:
    """
    Save all prompts to JSON file.

    Args:
        output_dir: Output directory path.
        prompts_data: Dictionary containing all prompts and metadata.

    Returns:
        Path to saved JSON file.
    """
    prompts_path = os.path.join(output_dir, "prompts.json")
    with open(prompts_path, "w", encoding="utf-8") as f:
        json.dump(prompts_data, f, ensure_ascii=False, indent=2)
    print(f"  Prompts saved: {prompts_path}")
    return prompts_path


# =============================================================================
# Main Entry Point
# =============================================================================

def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="PPT Generator - Generate PPT images using Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python generate_ppt.py --plan slides_plan.json --style styles/gradient-glass.md --resolution 2K

Environment variables:
  GEMINI_API_KEY: Google AI API key (required for the default provider)
  ATLASCLOUD_API_KEY: Atlas Cloud API key (required for --provider atlas)
  ATLASCLOUD_IMAGE_MODEL: override the Atlas model (default bytedance/seedream-v4)
""",
    )

    parser.add_argument(
        "--plan",
        required=True,
        help="Path to slides plan JSON file (generated by Skill)",
    )
    parser.add_argument(
        "--style",
        required=True,
        help="Path to style template file",
    )
    parser.add_argument(
        "--resolution",
        choices=["2K", "4K"],
        default=DEFAULT_RESOLUTION,
        help=f"Image resolution (default: {DEFAULT_RESOLUTION})",
    )
    parser.add_argument(
        "--provider",
        choices=["gemini", "atlas"],
        default="gemini",
        help="Image provider: gemini (default, Google AI) or atlas (Atlas Cloud)",
    )
    parser.add_argument(
        "--output",
        help="Output directory path (default: outputs/TIMESTAMP)",
    )
    parser.add_argument(
        "--template",
        default=DEFAULT_TEMPLATE_PATH,
        help=f"HTML template path (default: {DEFAULT_TEMPLATE_PATH})",
    )

    return parser


def main() -> None:
    """Main entry point for PPT generation."""
    # Load environment variables
    find_and_load_env()

    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args()

    # Load slides plan
    with open(args.plan, "r", encoding="utf-8") as f:
        slides_plan = json.load(f)

    # Load style template
    style_template = load_style_template(args.style)

    # Create output directory
    if args.output:
        output_dir = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"{OUTPUT_BASE_DIR}/{timestamp}"

    os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)

    # Print configuration
    slides = slides_plan["slides"]
    total_slides = len(slides)

    print("=" * 60)
    print("PPT Generator Started")
    print("=" * 60)
    print(f"Style: {args.style}")
    print(f"Resolution: {args.resolution}")
    print(f"Slides: {total_slides}")
    print(f"Output: {output_dir}")
    print("=" * 60)
    print()

    # Initialize prompts data
    prompts_data: Dict[str, Any] = {
        "metadata": {
            "title": slides_plan.get("title", "Untitled Presentation"),
            "total_slides": total_slides,
            "resolution": args.resolution,
            "style": args.style,
            "generated_at": datetime.now().isoformat(),
        },
        "slides": [],
    }

    # Generate each slide
    for slide_info in slides:
        slide_number = slide_info["slide_number"]
        page_type = slide_info.get("page_type", "content")
        content_text = slide_info["content"]

        # Generate prompt
        prompt = generate_prompt(
            style_template,
            page_type,
            content_text,
            slide_number,
            total_slides,
        )

        # Generate image
        image_path = generate_slide(
            prompt, slide_number, output_dir, args.resolution, args.provider
        )

        # Record prompt data
        prompts_data["slides"].append({
            "slide_number": slide_number,
            "page_type": page_type,
            "content": content_text,
            "prompt": prompt,
            "image_path": image_path,
        })

        print()

    # Save prompts
    save_prompts(output_dir, prompts_data)

    # Generate viewer HTML
    generate_viewer_html(output_dir, total_slides, args.template)

    # Print completion summary
    print()
    print("=" * 60)
    print("Generation Complete!")
    print("=" * 60)
    print(f"Output directory: {output_dir}")
    print(f"Viewer HTML: {os.path.join(output_dir, 'index.html')}")
    print()
    print("Open viewer in browser:")
    print(f"  open {os.path.join(output_dir, 'index.html')}")
    print()


if __name__ == "__main__":
    main()
