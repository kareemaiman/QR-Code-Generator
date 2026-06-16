# Development Rules for QR Generator GUI

To ensure the project remains functional, maintainable, and robust, adhere to the following development rules:

## 1. GUI Technologies
- Use Python's built-in `tkinter` and `ttk` libraries for the GUI to avoid adding unnecessary external dependencies, ensuring the app runs out-of-the-box.
- Use `Pillow` (PIL) for image manipulation, resizing, and rendering previews inside the GUI.
- Implement a modern, dark-themed styling system using standard Tkinter drawing and custom styles to make it look premium (no basic, standard grey Windows 95 widgets).

## 2. Code Structure
- Maintain separation between the QR Code generation logic and the GUI rendering logic.
- The generation logic should be flexible enough to support custom styles, colors, gradients, logo overlays, and arbitrary text input.
- Keep the main GUI loop and widgets organized in clean classes.

## 3. Error Handling & Robustness
- Gracefully handle file saving failures, invalid input data, and image format loading issues (e.g., when a user selects an unsupported logo image).
- Ensure preview generation is fast and non-blocking. Run background generation/previews safely.
- If logo image opening fails, display a user-friendly error dialog rather than crashing the application.
