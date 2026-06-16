# Code Wiki - QR Code Generator

## Project Goals
The goal of this project is to provide a versatile, aesthetically pleasing QR Code Generator. It allows users to encode text or URLs into QR codes and customize the visual style (colors, gradients, module shapes, and logo overlays in the center) via an intuitive, modern graphical user interface (GUI).

## Project Metadata
- **Current Version**: 1.0.0
- **Project Start Date**: June 16, 2026
- **Latest Update Date**: June 16, 2026
- **Programming Languages**: Python 3
- **Libraries Used**:
  - `qrcode` (for generating QR code matrices)
  - `Pillow` / `PIL` (for image manipulation, gradients, and logo overlays)
  - `tkinter` & `ttk` (for the GUI implementation)
- **Database Schema**: N/A (No database used)
- **Methodologies**: Object-Oriented Programming (OOP) for GUI components, modular functional programming for QR generation.

---

## File Structure & Functions

### File Structure
```
qr code generator/
├── QR_GEN.py        # Original CLI-based generator script
├── app.py           # GUI application entry point
├── dev_rules.md     # Development guidelines and styling rules
├── code_wiki.md     # This wiki document
├── README.md        # Project overview and usage guidelines
└── LICENSE          # MIT License agreement
```

### Classes and Functions in `app.py`
- **`extract_dominant_colors(image_path, num_colors=2)`**: Helper function that reads a logo image, analyzes its colors, filters for vibrancy/saturation, and returns the top dominant colors.
- **`QRGeneratorApp`**: The main GUI application class.
  - **`__init__(self, root)`**: Initializes GUI configurations, window geometry, color defaults, and themes.
  - **`setup_styles(self)`**: Configures clean, dark-themed styling for Tkinter widgets and panels.
  - **`create_settings_panel(self)`**: Builds the left configuration section containing input controls (style, gradient, colors, logo overlay, sliders).
  - **`create_preview_panel(self)`**: Builds the right interactive visualization canvas and the save button.
  - **`update_color_ui_state(self)`**: Toggles interactive state of secondary color based on solid vs gradient mask selection.
  - **`toggle_auto_color(self)`**: Automatically processes dominant colors from the uploaded logo if selected.
  - **`toggle_logo_options(self)`**: Hides or shows advanced logo customization options based on checkbox status.
  - **`upload_logo(self)`**: Opens a file dialog to allow users to select custom logo images.
  - **`extract_logo_colors(self)`**: Invokes the color extraction utility for dynamic gradient styling.
  - **`pick_color(self, target)`**: Opens an interactive color picker dialog to choose primary, secondary, or background colors.
  - **`get_qrcode_components(self)`**: Maps the user interface inputs to respective `qrcode` and `StyledPilImage` components (module drawers, masks, correction level).
  - **`generate_qr(self)`**: Executes QR generation, gradient rendering, overlay positioning, buffer calculation, and updates the preview canvas.
  - **`draw_preview(self)`**: Renders the generated QR image centered in the canvas while maintaining square aspect ratios and handling resize events.
  - **`save_qr(self)`**: Opens a file save dialog to export the high-definition QR code.
  - **`get_char_limit(self)`**: Calculates the max character capacity based on the selected error correction level.
  - **`update_char_count(self)`**: Calculates and displays current characters against the maximum allowable capacity, highlighting in red if exceeded.

### Functions in `QR_GEN.py`
This is a procedural script containing no formal functions, but performs the following logical steps:
1. **Configures paths & inputs**: Defines URL, logo path, and output file.
2. **Generates Base QR**: Sets high error correction (`ERROR_CORRECT_H`).
3. **Dominant Color Extraction**: Reads the logo and attempts to extract two vibrant colors for gradient mask generation.
4. **Applies Custom Gradient Mask**: Creates a `RadialGradiantColorMask`.
5. **Renders QR Code**: Uses `StyledPilImage` with `RoundedModuleDrawer`.
6. **Overlays Logo**: Centers the logo, drawing a white buffer circle underneath to hide background QR modules.
7. **Saves Image**: Exports the final image.

---

## Requirements Tracking

### Completed Requirements
- [x] Basic QR code generation from URL
- [x] Rounded module drawer style
- [x] Dominant color extraction from logo for gradient generation
- [x] Center logo overlay with white background circle buffer
- [x] Implement Graphical User Interface (GUI)
- [x] Add preview window in the GUI for real-time visualization
- [x] Support encoding arbitrary text, not just URLs
- [x] Interactive controls for QR styles (module drawers: Rounded, Square, Circle, etc.)
- [x] Interactive controls for colors/gradients (solid colors, radial/horizontal/vertical/square gradients)
- [x] Toggle logo overlay on/off, with option to select custom logo file
- [x] Ability to choose custom destination path for saving files
- [x] Dynamic auto-extraction configuration matching solid vs gradient mask selection
- [x] Logo buffer with extra visual spacing avoiding touching module squares
- [x] Safety constraint mechanism capping logo width dynamically against error correction limits
- [x] Dynamic character counting and limit labels for all error correction levels

