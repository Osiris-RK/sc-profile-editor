#!/usr/bin/env python
"""
Command-line tool to generate SVG overlay files from template images using OCR

Usage:
    python generate_svg_overlay.py <image_path> [output_path] [--profile profile.xml] [--joystick N]

The script will automatically look for a config.json file in the same directory as the
image. This config file can specify SVG styling options like font_family, font_size,
fill, and text_anchor. See vpc_mt50cm3_right/config.json for an example.

Optional profile argument will parse the Star Citizen profile XML to find all buttons
used for the specified joystick instance and add any unmapped buttons to a fallback table.

Example:
    python generate_svg_overlay.py visual-templates/EVO.png
    python generate_svg_overlay.py visual-templates/vpc_mt50cm3_right/vpc_mt50cm3_right.png --profile example-profiles/layout_VirpilOCT25_exported.xml --joystick 1
"""

import sys
import os
import logging
import argparse

# Setup logging for CLI
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.graphics.svg_generator import SVGOverlayGenerator


def main():
    parser = argparse.ArgumentParser(
        description='Generate SVG overlay files from template images using OCR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_svg_overlay.py visual-templates/EVO.png
  python generate_svg_overlay.py vpc_mt50cm3_right/vpc_mt50cm3_right.png -p layout_VirpilOCT25_exported.xml -j 1
        """
    )

    parser.add_argument('image_path', help='Path to template image')
    parser.add_argument('output_path', nargs='?', help='Path to save SVG (optional)')
    parser.add_argument('-p', '--profile', help='Path to Star Citizen profile XML')
    parser.add_argument('-j', '--joystick', type=int, default=1,
                       help='Joystick instance number (default: 1)')

    args = parser.parse_args()

    # Check if image exists
    if not os.path.exists(args.image_path):
        logger.error(f"Image file not found: {args.image_path}")
        sys.exit(1)

    # Check if profile exists (if specified)
    if args.profile and not os.path.exists(args.profile):
        logger.error(f"Profile file not found: {args.profile}")
        sys.exit(1)

    # Create generator
    generator = SVGOverlayGenerator()

    print(f"Generating SVG overlay for: {args.image_path}")

    # Check for config file
    image_dir = os.path.dirname(args.image_path)
    config_path = os.path.join(image_dir, 'config.json')
    if os.path.exists(config_path):
        print(f"Using config from: {config_path}")
    else:
        print("No config.json found, using default styling")

    if args.profile:
        print(f"Using profile: {args.profile} (joystick instance {args.joystick})")

    print("This may take a moment while OCR processes the image...")
    print()

    # Generate SVG (will auto-detect config.json in same directory)
    result_path = generator.generate_svg_overlay(
        args.image_path,
        args.output_path,
        profile_path=args.profile,
        joystick_instance=args.joystick
    )

    if result_path:
        print()
        print("=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"SVG overlay saved to: {result_path}")
        print()
        print("Next steps:")
        print("1. Open the SVG file in a text editor to review detected tags")
        print("2. Create/edit config.json to adjust font_size, fill, text_anchor")
        print("3. Re-run this script to regenerate SVG with new styling")
        print("4. Update template_registry.json to reference this SVG overlay")
        print()
        print("Example template_registry.json entry:")
        print('  {')
        print('    "id": "my_device",')
        print('    "name": "My Device Name",')
        print(f'    "image": "{os.path.basename(args.image_path)}",')
        print(f'    "overlay": "{os.path.basename(result_path)}",')
        print('    "device_match_patterns": ["Device Pattern"],')
        print('    "type": "joystick"')
        print('  }')
    else:
        logger.error("Failed to generate SVG overlay - make sure the image contains text in the format {{ Button X }}")
        sys.exit(1)


if __name__ == "__main__":
    main()
