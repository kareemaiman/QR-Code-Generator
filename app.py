import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import (
    RoundedModuleDrawer,
    SquareModuleDrawer,
    GappedSquareModuleDrawer,
    CircleModuleDrawer,
    VerticalBarsDrawer,
    HorizontalBarsDrawer
)
from qrcode.image.styles.colormasks import (
    SolidFillColorMask,
    RadialGradiantColorMask,
    SquareGradiantColorMask,
    HorizontalGradiantColorMask,
    VerticalGradiantColorMask
)
from PIL import Image, ImageDraw, ImageTk

# --- Color Extraction Helper ---
def extract_dominant_colors(image_path, num_colors=2):
    try:
        logo_src = Image.open(image_path).convert("RGB")
        logo_src.thumbnail((100, 100))  # Downscale for faster analysis
        w, h = logo_src.size
        # Use w * h * 10 to ensure getcolors never returns None
        colors = logo_src.getcolors(w * h * 10)
        if colors is None:
            colors = logo_src.getcolors(10000000)
            
        vibrant_colors = []
        for count, color in colors:
            r, g, b = color
            v = max(r, g, b)
            s = (max(r, g, b) - min(r, g, b)) / v if v != 0 else 0
            # Be slightly more permissive with saturation/vibrancy thresholds
            if v > 50 and s > 0.20:
                vibrant_colors.append((count, color))
                
        vibrant_colors.sort(key=lambda x: x[0], reverse=True)
        
        extracted = [c[1] for c in vibrant_colors[:num_colors]]
        while len(extracted) < num_colors:
            if len(extracted) == 1:
                r, g, b = extracted[0]
                # Create a nice secondary color by shifting the primary
                r2 = max(0, r - 60) if r > 127 else min(255, r + 60)
                g2 = max(0, g - 60) if g > 127 else min(255, g + 60)
                b2 = max(0, b - 60) if b > 127 else min(255, b + 60)
                extracted.append((r2, g2, b2))
            else:
                extracted.append((130, 40, 210))  # Default vibrant purple
        return extracted
    except Exception as e:
        print(f"Error extracting colors: {e}")
        return [(130, 40, 210), (80, 230, 60)]

class QRGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Premium QR Code Generator")
        self.root.geometry("1100x750")
        self.root.configure(bg="#121214")
        self.root.minsize(950, 650)
        
        # Default State variables
        self.primary_color = (31, 31, 36)      # default dark-ish/blue
        self.secondary_color = (139, 92, 246)  # default violet
        self.bg_color = (255, 255, 255)        # default white
        self.logo_path = ""
        self.current_qr_image = None
        
        # Configure Grid
        self.root.columnconfigure(0, weight=2, minsize=450)
        self.root.columnconfigure(1, weight=3, minsize=500)
        self.root.rowconfigure(0, weight=1)

        # Style configurations
        self.setup_styles()
        
        # Panels
        self.create_settings_panel()
        self.create_preview_panel()

        # Generate default preview on startup
        self.update_char_count()
        self.generate_qr()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure custom themes
        style.configure(".", background="#121214", foreground="#e2e8f0", font=("Segoe UI", 10))
        style.configure("TLabel", background="#121214", foreground="#e2e8f0")
        style.configure("Header.TLabel", font=("Segoe UI Semibold", 16), foreground="#ffffff")
        style.configure("SubHeader.TLabel", font=("Segoe UI Semibold", 12), foreground="#ffffff")
        
        style.configure("TFrame", background="#1a1a1e")
        style.configure("Settings.TFrame", background="#1a1a1e")
        style.configure("Preview.TFrame", background="#121214")
        
        # Checkbox & Radio styling
        style.configure("TCheckbutton", background="#1a1a1e", foreground="#e2e8f0")
        style.configure("TRadiobutton", background="#1a1a1e", foreground="#e2e8f0")
        
        # Custom button
        style.configure("Accent.TButton", background="#8b5cf6", foreground="#ffffff", borderwidth=0, font=("Segoe UI Semibold", 11))
        style.map("Accent.TButton", background=[("active", "#7c3aed"), ("pressed", "#6d28d9")])
        
        style.configure("Secondary.TButton", background="#313244", foreground="#ffffff", borderwidth=0, font=("Segoe UI", 10))
        style.map("Secondary.TButton", background=[("active", "#45475a"), ("pressed", "#585b70")])

    def create_settings_panel(self):
        # Settings Main Frame
        settings_frame = ttk.Frame(self.root, style="Settings.TFrame", padding=20)
        settings_frame.grid(row=0, column=0, sticky="nsew", padx=(15, 7), pady=15)
        
        # Enable scrollbar if content overflows
        canvas = tk.Canvas(settings_frame, bg="#1a1a1e", bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Settings.TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Handle mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title = ttk.Label(scrollable_frame, text="QR Code Designer", style="Header.TLabel")
        title.pack(anchor="w", pady=(0, 15))
        
        # 1. Text/Data Section
        data_lbl = ttk.Label(scrollable_frame, text="Content to Encode", style="SubHeader.TLabel")
        data_lbl.pack(anchor="w", pady=(10, 5))
        
        self.text_input = tk.Text(scrollable_frame, height=3, width=40, bg="#242428", fg="#f8fafc", insertbackground="#ffffff", bd=1, relief="flat", font=("Segoe UI", 10))
        self.text_input.insert("1.0", "https://github.com")
        self.text_input.pack(fill="x", pady=(0, 5))
        self.text_input.bind("<KeyRelease>", lambda e: self.update_char_count())
        
        self.char_count_lbl = ttk.Label(scrollable_frame, text="Characters: 18/1273", font=("Segoe UI", 9), foreground="#a6adc8")
        self.char_count_lbl.pack(anchor="w", pady=(0, 15))
        
        # Separator
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", pady=10)
        
        # 2. QR Style Customization
        style_lbl = ttk.Label(scrollable_frame, text="QR Design Style", style="SubHeader.TLabel")
        style_lbl.pack(anchor="w", pady=(5, 5))
        
        # Module Drawer selector
        ttk.Label(scrollable_frame, text="Module Style:").pack(anchor="w", pady=2)
        self.module_style_var = tk.StringVar(value="Rounded")
        styles_combo = ttk.Combobox(
            scrollable_frame, 
            textvariable=self.module_style_var, 
            values=["Square", "Rounded", "Circle", "Gapped Square", "Vertical Bars", "Horizontal Bars"],
            state="readonly"
        )
        styles_combo.pack(fill="x", pady=(0, 10))
        
        # Error correction level
        ttk.Label(scrollable_frame, text="Error Correction:").pack(anchor="w", pady=2)
        self.error_correction_var = tk.StringVar(value="High (30% - Best for Logos)")
        ec_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.error_correction_var,
            values=["Low (7%)", "Medium (15%)", "Quartile (25%)", "High (30% - Best for Logos)"],
            state="readonly"
        )
        ec_combo.pack(fill="x", pady=(0, 5))
        ec_combo.bind("<<ComboboxSelected>>", lambda e: [self.update_char_count(), self.generate_qr()])

        self.ec_note_lbl = ttk.Label(
            scrollable_frame,
            text="Note: Lower % allows encoding more text (max 2953 chars at 7%).\nHigher % is safer for logos but fits less text (max 1273 chars at 30%).",
            font=("Segoe UI Italic", 9),
            foreground="#a6adc8",
            justify="left"
        )
        self.ec_note_lbl.pack(anchor="w", pady=(0, 10))

        # Separator
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", pady=10)
        
        # 3. Colors & Gradients Section
        colors_lbl = ttk.Label(scrollable_frame, text="Colors & Gradients", style="SubHeader.TLabel")
        colors_lbl.pack(anchor="w", pady=(5, 5))
        
        # Mask Style Selection
        self.mask_type_var = tk.StringVar(value="Solid Color")
        mask_types = ["Solid Color", "Radial Gradient", "Square Gradient", "Horizontal Gradient", "Vertical Gradient"]
        mask_frame = ttk.Frame(scrollable_frame, style="Settings.TFrame")
        mask_frame.pack(fill="x", pady=(0, 10))
        for mt in mask_types:
            ttk.Radiobutton(mask_frame, text=mt, value=mt, variable=self.mask_type_var, command=self.update_color_ui_state).pack(anchor="w", pady=2)

        # Color picker buttons
        self.colors_button_frame = ttk.Frame(scrollable_frame, style="Settings.TFrame")
        self.colors_button_frame.pack(fill="x", pady=5)
        
        self.primary_btn = ttk.Button(self.colors_button_frame, text="Primary / Start Color", style="Secondary.TButton", command=lambda: self.pick_color("primary"))
        self.primary_btn.pack(fill="x", pady=2)
        
        self.secondary_btn = ttk.Button(self.colors_button_frame, text="Secondary / End Color (Gradients)", style="Secondary.TButton", command=lambda: self.pick_color("secondary"))
        self.secondary_btn.pack(fill="x", pady=2)
        
        self.bg_btn = ttk.Button(self.colors_button_frame, text="Background Color", style="Secondary.TButton", command=lambda: self.pick_color("bg"))
        self.bg_btn.pack(fill="x", pady=2)
        
        # Dynamic extraction from logo check
        self.auto_color_var = tk.BooleanVar(value=False)
        self.auto_color_check = ttk.Checkbutton(
            scrollable_frame, 
            text="Auto-extract colors from Logo", 
            variable=self.auto_color_var,
            command=self.toggle_auto_color
        )
        self.auto_color_check.pack(anchor="w", pady=5)
        
        # Separator
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", pady=10)
        
        # 4. Logo Settings
        logo_lbl = ttk.Label(scrollable_frame, text="Logo Overlay", style="SubHeader.TLabel")
        logo_lbl.pack(anchor="w", pady=(5, 5))
        
        self.enable_logo_var = tk.BooleanVar(value=False)
        self.enable_logo_check = ttk.Checkbutton(
            scrollable_frame, 
            text="Enable Center Logo", 
            variable=self.enable_logo_var,
            command=self.toggle_logo_options
        )
        self.enable_logo_check.pack(anchor="w", pady=2)
        
        self.logo_controls_frame = ttk.Frame(scrollable_frame, style="Settings.TFrame")
        
        self.logo_path_lbl = ttk.Label(self.logo_controls_frame, text="No file selected", font=("Segoe UI Italic", 9))
        self.logo_path_lbl.pack(anchor="w", pady=2)
        
        self.upload_btn = ttk.Button(self.logo_controls_frame, text="Choose Logo Image...", style="Secondary.TButton", command=self.upload_logo)
        self.upload_btn.pack(fill="x", pady=2)
        
        ttk.Label(self.logo_controls_frame, text="Logo Size Ratio (% of QR width):").pack(anchor="w", pady=(5, 2))
        self.logo_size_slider = ttk.Scale(self.logo_controls_frame, from_=15, to=40, value=28, orient="horizontal")
        self.logo_size_slider.pack(fill="x", pady=(0, 10))
        
        # Separator
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", pady=10)
        
        # Update/Generate Button
        self.update_btn = ttk.Button(scrollable_frame, text="Update Preview", style="Accent.TButton", command=self.generate_qr)
        self.update_btn.pack(fill="x", pady=(10, 10), ipady=5)

    def create_preview_panel(self):
        # Preview Main Frame
        preview_frame = ttk.Frame(self.root, style="Preview.TFrame")
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=(7, 15), pady=15)
        
        # Center Preview box
        container = ttk.Frame(preview_frame, style="Settings.TFrame", padding=20)
        container.pack(expand=True, fill="both")
        
        title = ttk.Label(container, text="Live Preview", style="SubHeader.TLabel")
        title.pack(anchor="w", pady=(0, 10))
        
        self.preview_canvas = tk.Canvas(container, bg="#242428", bd=0, highlightthickness=0)
        self.preview_canvas.pack(expand=True, fill="both", padx=10, pady=10)
        self.preview_canvas.bind("<Configure>", self.on_preview_resize)
        
        # Action controls below preview
        actions_frame = ttk.Frame(container, style="Settings.TFrame")
        actions_frame.pack(fill="x", pady=(10, 0))
        
        self.save_btn = ttk.Button(actions_frame, text="Export / Save QR Code", style="Accent.TButton", command=self.save_qr)
        self.save_btn.pack(fill="x", ipady=5)

    def update_color_ui_state(self):
        # Enable or disable secondary color based on mask selection
        mask_type = self.mask_type_var.get()
        if mask_type == "Solid Color":
            self.secondary_btn.configure(state="disabled")
        else:
            if not self.auto_color_var.get():
                self.secondary_btn.configure(state="normal")
        
        # Re-extract colors if auto color is active when mask type changes
        if self.auto_color_var.get():
            self.extract_logo_colors()
            
        self.generate_qr()

    def toggle_auto_color(self):
        if self.auto_color_var.get():
            self.primary_btn.configure(state="disabled")
            self.secondary_btn.configure(state="disabled")
            if self.logo_path:
                self.extract_logo_colors()
                self.generate_qr()
        else:
            self.primary_btn.configure(state="normal")
            self.update_color_ui_state()
            self.generate_qr()

    def toggle_logo_options(self):
        if self.enable_logo_var.get():
            self.logo_controls_frame.pack(fill="x", pady=(5, 10))
        else:
            self.logo_controls_frame.pack_forget()

    def upload_logo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp *.gif"), ("All Files", "*.*")]
        )
        if file_path:
            self.logo_path = file_path
            self.logo_path_lbl.configure(text=os.path.basename(file_path))
            if self.auto_color_var.get():
                self.extract_logo_colors()
            self.generate_qr()

    def extract_logo_colors(self):
        if self.logo_path:
            mask_type = self.mask_type_var.get()
            if mask_type == "Solid Color":
                colors = extract_dominant_colors(self.logo_path, 1)
                self.primary_color = colors[0]
            else:
                colors = extract_dominant_colors(self.logo_path, 2)
                self.primary_color = colors[0]
                self.secondary_color = colors[1]
            print(f"Extracted Dominant Colors: Primary {self.primary_color}, Secondary {self.secondary_color}")

    def pick_color(self, target):
        initial = "#ffffff"
        if target == "primary":
            initial = '#%02x%02x%02x' % self.primary_color
        elif target == "secondary":
            initial = '#%02x%02x%02x' % self.secondary_color
        elif target == "bg":
            initial = '#%02x%02x%02x' % self.bg_color

        color = colorchooser.askcolor(initialcolor=initial)
        if color[0]:
            rgb = tuple(int(x) for x in color[0])
            if target == "primary":
                self.primary_color = rgb
            elif target == "secondary":
                self.secondary_color = rgb
            elif target == "bg":
                self.bg_color = rgb
            self.generate_qr()

    def on_preview_resize(self, event):
        self.draw_preview()

    def get_qrcode_components(self):
        # 1. Module style
        drawer_name = self.module_style_var.get()
        if drawer_name == "Square":
            drawer = SquareModuleDrawer()
        elif drawer_name == "Rounded":
            drawer = RoundedModuleDrawer()
        elif drawer_name == "Circle":
            drawer = CircleModuleDrawer()
        elif drawer_name == "Gapped Square":
            drawer = GappedSquareModuleDrawer()
        elif drawer_name == "Vertical Bars":
            drawer = VerticalBarsDrawer()
        elif drawer_name == "Horizontal Bars":
            drawer = HorizontalBarsDrawer()
        else:
            drawer = RoundedModuleDrawer()

        # 2. Color mask
        mask_type = self.mask_type_var.get()
        p_color = self.primary_color
        s_color = self.secondary_color
        bg_color = self.bg_color

        if mask_type == "Solid Color":
            mask = SolidFillColorMask(back_color=bg_color, front_color=p_color)
        elif mask_type == "Radial Gradient":
            mask = RadialGradiantColorMask(back_color=bg_color, center_color=s_color, edge_color=p_color)
        elif mask_type == "Square Gradient":
            mask = SquareGradiantColorMask(back_color=bg_color, center_color=s_color, edge_color=p_color)
        elif mask_type == "Horizontal Gradient":
            mask = HorizontalGradiantColorMask(back_color=bg_color, left_color=p_color, right_color=s_color)
        elif mask_type == "Vertical Gradient":
            mask = VerticalGradiantColorMask(back_color=bg_color, top_color=p_color, bottom_color=s_color)
        else:
            mask = SolidFillColorMask(back_color=bg_color, front_color=p_color)

        # 3. Error correction
        ec_val = self.error_correction_var.get()
        if "Low" in ec_val:
            ec = qrcode.constants.ERROR_CORRECT_L
        elif "Medium" in ec_val:
            ec = qrcode.constants.ERROR_CORRECT_M
        elif "Quartile" in ec_val:
            ec = qrcode.constants.ERROR_CORRECT_Q
        else:
            ec = qrcode.constants.ERROR_CORRECT_H

        return drawer, mask, ec

    def generate_qr(self):
        text_data = self.text_input.get("1.0", tk.END).strip()
        if not text_data:
            text_data = "https://github.com"

        drawer, mask, ec = self.get_qrcode_components()

        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=ec,
                box_size=12,
                border=4
            )
            qr.add_data(text_data)
            qr.make(fit=True)

            # Render styled image
            qr_img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=drawer,
                color_mask=mask
            ).convert("RGB")

            # Apply Logo Overlay if enabled
            if self.enable_logo_var.get() and self.logo_path and os.path.exists(self.logo_path):
                qr_width, qr_height = qr_img.size
                logo = Image.open(self.logo_path)
                
                # Dynamic error correction limit check:
                # L: 7% (0.07), M: 15% (0.15), Q: 25% (0.25), H: 30% (0.30)
                limit_map = {
                    qrcode.constants.ERROR_CORRECT_L: 0.07,
                    qrcode.constants.ERROR_CORRECT_M: 0.15,
                    qrcode.constants.ERROR_CORRECT_Q: 0.25,
                    qrcode.constants.ERROR_CORRECT_H: 0.30,
                }
                ec_limit = limit_map.get(ec, 0.30)
                
                # Set a safety margin of 10% on the EC limit
                max_safe_mask_ratio = (ec_limit ** 0.5) * 0.9
                
                # Logo buffer is 20% of logo width: mask_size = logo_width * 1.20
                # Thus, logo_width * 1.20 <= qr_width * max_safe_mask_ratio
                max_logo_ratio = max_safe_mask_ratio / 1.20
                
                # Scale logo based on slider percentage
                ratio = self.logo_size_slider.get() / 100.0
                
                # Automatically cap the logo ratio to respect the EC limit + buffer space
                if ratio > max_logo_ratio:
                    ratio = max_logo_ratio
                    self.logo_size_slider.set(int(max_logo_ratio * 100))
                
                logo_max_size = int(qr_width * ratio)
                logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
                logo_width, logo_height = logo.size
                
                paste_position = (
                    (qr_width - logo_width) // 2,
                    (qr_height - logo_height) // 2
                )
                
                # Clear background behind the logo (circle buffer) with extra spacing (20% margin)
                buffer_margin = int(logo_width * 0.20)
                mask_size = (logo_width + buffer_margin, logo_height + buffer_margin)
                mask_position = (
                    (qr_width - mask_size[0]) // 2,
                    (qr_height - mask_size[1]) // 2
                )
                
                draw = ImageDraw.Draw(qr_img)
                draw.ellipse(
                    [mask_position[0], mask_position[1], mask_position[0] + mask_size[0], mask_position[1] + mask_size[1]],
                    fill=self.bg_color
                )
                
                # Paste Logo
                if logo.mode in ('RGBA', 'LA') or (logo.mode == 'P' and 'transparency' in logo.info):
                    qr_img.paste(logo, paste_position, logo.convert('RGBA'))
                else:
                    qr_img.paste(logo, paste_position)

            self.current_qr_image = qr_img
            self.draw_preview()

        except Exception as e:
            messagebox.showerror("QR Code Error", f"An error occurred while generating the QR code:\n{str(e)}")

    def get_char_limit(self):
        ec_val = self.error_correction_var.get()
        if "Low" in ec_val:
            return 2953
        elif "Medium" in ec_val:
            return 2331
        elif "Quartile" in ec_val:
            return 1663
        else:
            return 1273

    def update_char_count(self):
        text_data = self.text_input.get("1.0", tk.END).strip()
        length = len(text_data)
        limit = self.get_char_limit()
        self.char_count_lbl.configure(text=f"Characters: {length}/{limit}")
        if length > limit:
            self.char_count_lbl.configure(foreground="#f38ba8")
        else:
            self.char_count_lbl.configure(foreground="#a6adc8")

    def draw_preview(self):
        if self.current_qr_image is None:
            return
        
        # Get canvas size
        canvas_w = self.preview_canvas.winfo_width()
        canvas_h = self.preview_canvas.winfo_height()
        
        # Use default dimensions if canvas isn't fully initialized yet
        if canvas_w < 50 or canvas_h < 50:
            canvas_w = 400
            canvas_h = 400

        # Maintain aspect ratio (QR codes are square)
        side = min(canvas_w, canvas_h) - 40
        if side < 100:
            side = 100
            
        # Resize image for preview
        preview_img = self.current_qr_image.resize((side, side), Image.Resampling.LANCZOS)
        self.tk_preview_img = ImageTk.PhotoImage(preview_img)
        
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(
            canvas_w // 2,
            canvas_h // 2,
            image=self.tk_preview_img,
            anchor="center"
        )

    def save_qr(self):
        if self.current_qr_image is None:
            messagebox.showwarning("Save QR Code", "Please generate a QR code first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                self.current_qr_image.save(file_path)
                messagebox.showinfo("Success", f"QR Code successfully saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error Saving", f"Failed to save image:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()
