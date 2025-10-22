# Mouse Template

This directory contains visual templates for gaming mice.

## Required Files

- **Device image**: Base image of a mouse (e.g., `mouse_generic.png`)
- **Template image**: Annotated version showing button locations
- **Overlay SVG**: SVG overlay file for mapping controls onto the mouse image

## Device Information

- **Type**: Mouse
- **Instance**: Typically instance 1 in Star Citizen profiles

## Notes

- Consider creating templates for different mouse types (2-button, 3-button, MMO mice with many buttons)
- The mouse template should show:
  - Left/Right mouse buttons
  - Middle mouse button (scroll wheel click)
  - Additional side buttons (if applicable)
  - Scroll wheel up/down

## Match Patterns

When adding to `template_registry.json`, use patterns like:
- "Mouse"
- "Gaming Mouse"