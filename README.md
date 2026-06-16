# Premium QR Code Generator with Custom Aesthetics

A highly-customizable, modern, dark-themed QR Code Generator built in Python. This tool gives you complete control over style, design layout, colors, and logos to generate premium-looking QR codes for websites, social media, branding, and text data.

---

## ✨ Features

- **Modern Graphical User Interface (GUI)**: Clean, interactive dark-themed layout built with `tkinter` and styled to modern UI standards.
- **Dynamic Live Preview**: See modifications in real-time on the canvas before exporting.
- **Advanced Module Shapes**: Choose module styles such as `Rounded`, `Circle`, `Square`, `Gapped Square`, `Vertical Bars`, or `Horizontal Bars`.
- **Flexible Color Modes**:
  - Solid fill colors.
  - Multi-directional gradients: `Radial`, `Square`, `Horizontal`, and `Vertical` gradients.
- **Smart Logo Overlay**:
  - Upload custom logo images to center inside the QR code.
  - **Dynamic Scaling & Capping**: Automatically prevents the logo size from exceeding the error correction threshold to ensure the QR remains 100% readable.
  - **Extra Buffer Margin**: Clears a clean circle buffer with extra space around the logo so it never touches the module squares.
- **Auto-Extract Dominant Colors**: Scans your uploaded logo and extracts either 1 color (for solid fills) or the top 2 vibrant colors (for gradient directions) automatically.
- **Live Character Limits & Counters**: Displays text length bounds for all error correction levels (Low, Medium, Quartile, High) and colors the indicator red if text exceeds limits.
- **Export Control**: Save your design locally in high-definition formats (PNG, JPEG).

---

## 🛠️ Installation

Ensure you have Python 3 installed. Clone the repository and install the dependencies:

```bash
# Clone the repository
git clone https://github.com/kareemaiman/QR-Code-Generator.git
cd QR-Code-Generator

# Install required packages
pip install qrcode pillow
```

---

## 🚀 How to Run

Launch the graphical designer interface by running the following command:

```bash
python app.py
```

---

## 🎨 Controls & Usage Guide

1. **Content to Encode**: Type or paste any text or URL. Watch the character counter update dynamically (e.g. `100/1273`).
2. **Error Correction Level**:
   - **Low (7%)**: Encodes up to 2953 characters (best for large text).
   - **Medium (15%)**: Encodes up to 2331 characters.
   - **Quartile (25%)**: Encodes up to 1663 characters.
   - **High (30%)**: Encodes up to 1273 characters (recommended when overlaying center logos).
3. **Design Styling**: Select module drawers, select gradient/solid fills, and open color pickers to customize your background and code colors.
4. **Logo Overlay**: Check the "Enable Center Logo" option, select a logo image, and adjust the scaling slider. If "Auto-extract colors" is enabled, the QR code gradients will automatically match your logo's dominant palette.
5. **Save**: Click "Export / Save QR Code" to export the generated output as an image.

---

## 📦 Project Structure

- `app.py`: Main GUI application entry point.
- `QR_GEN.py`: Original CLI-based implementation.
- `dev_rules.md`: Developer guidelines for styling and architecture.
- `code_wiki.md`: Code wiki documenting file structure, functions, classes, and libraries.
