# Keyboard Template

This directory contains visual templates for standard keyboards.

## Required Files

- **Device image**: Base image of a keyboard layout (e.g., `keyboard_104.png` for full-size)
- **Template image**: Annotated version showing key locations
- **Overlay SVG**: SVG overlay file for mapping controls onto the keyboard image

## Device Information

- **Type**: Keyboard
- **Instance**: Typically instance 1 in Star Citizen profiles
- **Product ID**: `{6F1D2B61-D5A0-11CF-BFC7-444553540000}` (standard Windows keyboard)

## Notes

- Consider creating templates for different keyboard layouts (ANSI, ISO, 60%, TKL, etc.)
- The keyboard template should clearly show all keys that can be bound in Star Citizen
- Common keys: WASD, Space, Ctrl, Shift, Alt, Function keys, Number pad, Arrow keys

## Match Patterns

When adding to `template_registry.json`, use patterns like:
- "Keyboard"
- "Standard Keyboard"