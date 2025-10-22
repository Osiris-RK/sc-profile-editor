# Visual Template Configuration Guide

## Overview

Each device template directory can contain a `config.json` file to customize how SVG overlays are generated. This allows you to easily adjust text styling without manually editing the SVG file.

## Config File Location

Place `config.json` in the same directory as your template image:

```
visual-templates/
├── vpc_mt50cm3_right/
│   ├── vpc_mt50cm3_right.png          # Template image
│   ├── vpc_mt50cm3_right_overlay.svg  # Generated SVG overlay
│   └── config.json                     # Styling configuration
```

## Config File Format

```json
{
  "device_name": "Device Name (optional)",
  "svg_style": {
    "font_family": "Arial",
    "font_size": 10,
    "fill": "black",
    "text_anchor": "middle",
    "stroke": null,
    "stroke_width": null,
    "text_wrap": {
      "enabled": false,
      "max_words_per_line": 2,
      "line_spacing": 1.2
    },
    "background": {
      "enabled": false,
      "fill": "white",
      "opacity": 0.8,
      "padding": 2,
      "border_radius": 2
    }
  },
  "description": "Optional description"
}
```

## SVG Style Options

### Basic Text Styling

#### `font_family` (string)
Font family for text labels. Common options:
- `"Arial"` (default)
- `"Helvetica"`
- `"Times New Roman"`
- `"Courier New"`
- `"Verdana"`

#### `font_size` (number)
Font size in pixels. Default: `10`

Examples:
- `8` - Small text
- `10` - Default
- `12` - Medium text
- `14` - Large text

#### `fill` (string)
Text color. Can be:
- Color names: `"black"`, `"white"`, `"red"`, `"blue"`, etc.
- Hex codes: `"#000000"`, `"#FFFFFF"`, `"#FF0000"`, etc.
- RGB: `"rgb(0, 0, 0)"`

Default: `"black"`

#### `text_anchor` (string)
Horizontal text alignment relative to the x,y position:
- `"start"` - Left aligned
- `"middle"` - Center aligned (default)
- `"end"` - Right aligned

### Text Outline/Stroke

#### `stroke` (string or null)
Adds an outline around text characters. Set to a color or `null` for no stroke.

Examples:
- `"white"` - White outline
- `"#000000"` - Black outline
- `null` - No outline (default)

**Common use case**: Black text with white stroke for readability on any background.

#### `stroke_width` (number or null)
Width of the stroke outline in pixels. Requires `stroke` to be set.

Examples:
- `1` - Thin outline
- `2` - Medium outline (recommended)
- `3` - Thick outline
- `null` - No stroke width (default)

### Text Wrapping

The `text_wrap` object controls multi-line text layout.

#### `text_wrap.enabled` (boolean)
Set to `true` to wrap text across multiple lines. Default: `false`

**Use case**: Labels like "{{ Button 1 }}" can become:
```
{{ Button
1 }}
```

#### `text_wrap.max_words_per_line` (number)
Maximum number of words per line. Default: `2`

Examples:
- `1` - One word per line
- `2` - Two words per line (default)
- `3` - Three words per line

**Example**: With `max_words_per_line: 2`:
- "{{ Button 1 }}" → stays as one line (2 words)
- "{{ Axis X Positive }}" → becomes 2 lines: "{{ Axis X" and "Positive }}"

#### `text_wrap.line_spacing` (number)
Multiplier for line height spacing. Default: `1.2`

Examples:
- `1.0` - Lines touching (font size)
- `1.2` - Normal spacing (default, 120% of font size)
- `1.5` - Generous spacing (150% of font size)

### Background Rectangle

The `background` object controls a colored rectangle drawn behind the text.

#### `background.enabled` (boolean)
Set to `true` to draw a background rectangle behind text. Default: `false`

#### `background.fill` (string)
Background color. Default: `"white"`

Examples:
- `"white"` - White background
- `"#000000"` - Black background
- `"rgba(255, 255, 255, 0.9)"` - White with transparency

#### `background.opacity` (number)
Background transparency from 0.0 (invisible) to 1.0 (solid). Default: `0.8`

Examples:
- `0.5` - Semi-transparent
- `0.8` - Mostly opaque (default)
- `1.0` - Fully opaque

#### `background.padding` (number)
Space around text in pixels. Default: `2`

Examples:
- `1` - Tight padding
- `2` - Normal padding (default)
- `4` - Generous padding

#### `background.border_radius` (number)
Rounded corners in pixels. Default: `2`

Examples:
- `0` - Square corners
- `2` - Slightly rounded (default)
- `5` - Very rounded

## Usage Workflow

1. **Create your template image** with labels like `{{ Button 1 }}`, `{{ Axis X }}`, etc.

2. **Run the SVG generator**:
   ```bash
   python visual-templates/generate_svg_overlay.py visual-templates/your_device/your_device.png
   ```

3. **Review the generated SVG** to see default styling

4. **Create or edit config.json** in the same directory:
   ```json
   {
     "svg_style": {
       "font_family": "Arial",
       "font_size": 12,
       "fill": "#333333",
       "text_anchor": "middle"
     }
   }
   ```

5. **Regenerate the SVG** with your new styling:
   ```bash
   python visual-templates/generate_svg_overlay.py visual-templates/your_device/your_device.png
   ```

6. **Repeat steps 4-5** until you're happy with the styling

## Example Configurations

### Black Text with White Outline (Works on any background)
```json
{
  "svg_style": {
    "font_family": "Arial",
    "font_size": 10,
    "fill": "black",
    "text_anchor": "middle",
    "stroke": "white",
    "stroke_width": 2
  }
}
```

### White Text with Black Outline
```json
{
  "svg_style": {
    "font_family": "Arial",
    "font_size": 10,
    "fill": "white",
    "text_anchor": "middle",
    "stroke": "black",
    "stroke_width": 2
  }
}
```

### Text with Semi-Transparent Background
```json
{
  "svg_style": {
    "font_family": "Arial",
    "font_size": 10,
    "fill": "black",
    "text_anchor": "middle",
    "background": {
      "enabled": true,
      "fill": "white",
      "opacity": 0.7,
      "padding": 3,
      "border_radius": 3
    }
  }
}
```

### Text with Background AND Stroke (Maximum readability)
```json
{
  "svg_style": {
    "font_family": "Arial",
    "font_size": 10,
    "fill": "black",
    "text_anchor": "middle",
    "stroke": "white",
    "stroke_width": 1,
    "background": {
      "enabled": true,
      "fill": "yellow",
      "opacity": 0.6,
      "padding": 2,
      "border_radius": 2
    }
  }
}
```

### Small Labels
```json
{
  "svg_style": {
    "font_family": "Arial",
    "font_size": 8,
    "fill": "black",
    "text_anchor": "middle"
  }
}
```

### Left-Aligned Labels
```json
{
  "svg_style": {
    "font_family": "Arial",
    "font_size": 10,
    "fill": "black",
    "text_anchor": "start"
  }
}
```

### Multi-Line Text with Wrapping
```json
{
  "svg_style": {
    "font_family": "Arial",
    "font_size": 10,
    "fill": "black",
    "text_anchor": "middle",
    "text_wrap": {
      "enabled": true,
      "max_words_per_line": 2,
      "line_spacing": 1.3
    }
  }
}
```

### Compact Multi-Line with Background
```json
{
  "svg_style": {
    "font_family": "Arial",
    "font_size": 9,
    "fill": "black",
    "text_anchor": "middle",
    "text_wrap": {
      "enabled": true,
      "max_words_per_line": 1,
      "line_spacing": 1.1
    },
    "background": {
      "enabled": true,
      "fill": "white",
      "opacity": 0.85,
      "padding": 3,
      "border_radius": 2
    }
  }
}
```

## Advanced: Per-Element Styling

If you need different styling for individual elements, you can:
1. Generate the SVG with config.json
2. Manually edit the SVG file to adjust specific `<text>` elements
3. Keep the config.json for reference and regeneration

## See Also

- Example: `visual-templates/vpc_mt50cm3_right/config.json`
- SVG Generator: `visual-templates/generate_svg_overlay.py`
