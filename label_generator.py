import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
import sys

class SheetMetalLabelGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Sheet Metal Label Generator")
        self.root.configure(bg="#f5f5f5")

        # Font handling
        try:
            self.font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
            if not os.path.exists(self.font_path):
                print(f"Font file not found at {self.font_path}, falling back to Helvetica.")
                self.font_path = "/System/Library/Fonts/Helvetica.ttc"
            if not os.path.exists(self.font_path):
                raise FileNotFoundError("Helvetica not found either.")
            self.large_font = ImageFont.truetype(self.font_path, 154)  # 154pt for color title
            self.medium_font = ImageFont.truetype(self.font_path, 100)  # 100pt for material/gauge and status
            print("Fonts loaded successfully: Arial/Helvetica at 154pt and 100pt.")
        except Exception as e:
            print(f"Error loading font: {e}")
            self.large_font = ImageFont.load_default()
            self.medium_font = ImageFont.load_default()
            print("Using default Pillow font as fallback (sizes may be small).")

        # Variables
        self.color_var = tk.StringVar(value="Snowdrift White")
        self.material_var = tk.StringVar(value="Galvalume")
        self.gauge_var = tk.StringVar(value="24ga")
        self.status_var = tk.StringVar(value="Open")
        self.project_var = tk.StringVar(value="")
        self.custom_color_value = tk.StringVar(value="#000000")  # Default black for color picker
        self.mill_finish_image = None

        # Color mappings
        self.color_map = {
            "Snowdrift White": (239, 240, 241), "Bone White": (225, 225, 212),
            "Regal White": (227, 231, 230), "Stone White": (223, 225, 222),
            "Medium Bronze": (89, 79, 68), "Almond": (211, 203, 183),
            "Sandstone": (196, 194, 177), "Sierra Tan": (163, 143, 124),
            "Dark Bronze": (58, 54, 53), "Aged Copper": (138, 169, 142),
            "Dove Gray": (143, 147, 145), "Ash Gray": (163, 159, 149),
            "Slate Gray": (118, 117, 111), "Charcoal Gray": (83, 86, 88),
            "Patina Green": (123, 133, 112), "Evergreen": (55, 82, 69),
            "Slate Blue": (84, 118, 132), "Regal Blue": (38, 80, 105),
            "Banner Red": (159, 36, 50), "Colonial Red": (111, 52, 46),
            "Terra Cotta": (154, 74, 57), "Mansard Brown": (72, 56, 51),
            "Matte Black": (48, 49, 47), "Mill Finish": (204, 204, 204),
            "Bright Silver": "gradient", "Pre-Weathered": "gradient",
            "Copper Penny": "gradient"
        }

        # Gradient definitions
        self.gradient_map = {
            "Bright Silver": [(189, 193, 196), (240, 240, 240), (189, 193, 196)],
            "Pre-Weathered": [(129, 133, 136), (99, 99, 99), (129, 133, 136)],
            "Copper Penny": [(172, 113, 71), (215, 125, 19), (172, 113, 71)]
        }

        self.create_widgets()

    def create_widgets(self):
        print("Creating widgets...")
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True)

        # Input frame (left side)
        self.input_frame = ttk.Frame(container)
        self.input_frame.pack(side="left", fill="y")

        # Color
        self.color_label = tk.Label(self.input_frame, text="Color:", font=("Helvetica", 14, "bold"), fg="white")
        self.color_label.pack(fill="x")
        print("Color label set to bold Helvetica 14, white")
        color_options = list(self.color_map.keys()) + ["Other"]
        self.color_menu = ttk.Combobox(self.input_frame, textvariable=self.color_var, values=color_options, state="readonly")
        self.color_menu.pack(fill="x")
        self.color_menu.bind("<<ComboboxSelected>>", self.on_color_change)

        self.custom_color_entry = ttk.Entry(self.input_frame, width=30)
        self.color_picker_button = ttk.Button(self.input_frame, text="Pick Color", command=self.pick_color)
        self.mill_finish_button = ttk.Button(self.input_frame, text="Upload Mill Finish Image", command=self.upload_mill_finish)

        # Material
        self.material_label = tk.Label(self.input_frame, text="Material:", font=("Helvetica", 14, "bold"), fg="white")
        self.material_label.pack(fill="x")
        print("Material label set to bold Helvetica 14, white")
        material_options = ["Aluminum", "Steel", "Copper", "Galvalume", "Other"]
        self.material_menu = ttk.Combobox(self.input_frame, textvariable=self.material_var, values=material_options, state="readonly")
        self.material_menu.pack(fill="x")
        self.material_menu.bind("<<ComboboxSelected>>", self.on_material_change)

        self.custom_material_entry = ttk.Entry(self.input_frame, width=30)
        self.custom_material_entry.pack(fill="x")
        self.custom_material_entry.pack_forget()

        # Gauge
        self.gauge_label = tk.Label(self.input_frame, text="Gauge:", font=("Helvetica", 14, "bold"), fg="white")
        self.gauge_label.pack(fill="x")
        print("Gauge label set to bold Helvetica 14, white")
        gauge_options = ["24ga", ".032", "22ga", "Other"]
        self.gauge_menu = ttk.Combobox(self.input_frame, textvariable=self.gauge_var, values=gauge_options, state="readonly")
        self.gauge_menu.pack(fill="x")
        self.gauge_menu.bind("<<ComboboxSelected>>", self.on_gauge_change)

        self.custom_gauge_entry = ttk.Entry(self.input_frame, width=30)
        self.custom_gauge_entry.pack(fill="x")
        self.custom_gauge_entry.pack_forget()

        # Status
        self.status_label = tk.Label(self.input_frame, text="Status:", font=("Helvetica", 14, "bold"), fg="white")
        self.status_label.pack(fill="x")
        print("Status label set to bold Helvetica 14, white")
        self.status_menu = ttk.Combobox(self.input_frame, textvariable=self.status_var, values=["Open", "Reserved"], state="readonly")
        self.status_menu.pack(fill="x")
        self.status_menu.bind("<<ComboboxSelected>>", self.on_status_change)

        # Project Name (below Status)
        self.project_frame = ttk.Frame(self.input_frame)
        self.project_label = tk.Label(self.project_frame, text="Project Name:", font=("Helvetica", 14, "bold"), fg="white")
        self.project_label.pack(fill="x")
        print("Project Name label set to bold Helvetica 14, white")
        self.project_entry = ttk.Entry(self.project_frame, textvariable=self.project_var)
        self.project_entry.pack(fill="x")
        self.project_frame.pack(fill="x")
        self.project_frame.pack_forget()

        # Buttons
        self.generate_button = ttk.Button(self.input_frame, text="Generate Label", command=self.generate_label)
        self.generate_button.pack(fill="x")
        self.save_button = ttk.Button(self.input_frame, text="Save Label", command=self.save_label)
        self.save_button.pack(fill="x")

        # Preview frame (right side)
        self.preview_frame = ttk.Frame(container, relief="solid", borderwidth=1)
        self.preview_frame.pack(side="right", fill="both", expand=True)
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(expand=True)
        print("Widgets created.")

    def pick_color(self):
        color = colorchooser.askcolor(title="Choose Swatch Color", initialcolor=self.custom_color_value.get())
        if color[1]:  # If a color was selected
            self.custom_color_value.set(color[1])  # Hex value
            print(f"Color picked: {color[1]}")
            self.generate_label()

    def on_color_change(self, event):
        color = self.color_var.get()
        self.custom_color_entry.pack_forget()
        self.color_picker_button.pack_forget()
        self.mill_finish_button.pack_forget()
        if color == "Other":
            self.custom_color_entry.pack(fill="x", after=self.color_menu)
            self.color_picker_button.pack(fill="x", after=self.custom_color_entry)
            print("Custom color entry and picker packed below Color menu")
        elif color == "Mill Finish":
            self.mill_finish_button.pack(fill="x", after=self.color_menu)
            print("Mill finish button packed below Color menu")
        self.generate_label()

    def on_material_change(self, event):
        material = self.material_var.get()
        if material == "Other":
            self.custom_material_entry.pack(fill="x")
        else:
            self.custom_material_entry.pack_forget()
        self.generate_label()

    def on_gauge_change(self, event):
        gauge = self.gauge_var.get()
        if gauge == "Other":
            self.custom_gauge_entry.pack(fill="x")
        else:
            self.custom_gauge_entry.pack_forget()
        self.generate_label()

    def on_status_change(self, event):
        status = self.status_var.get()
        for widget in self.input_frame.winfo_children():
            widget.pack_forget()
        self.color_label.pack(fill="x")
        self.color_menu.pack(fill="x")
        if self.color_var.get() == "Other":
            self.custom_color_entry.pack(fill="x")
            self.color_picker_button.pack(fill="x")
        elif self.color_var.get() == "Mill Finish":
            self.mill_finish_button.pack(fill="x")
        self.material_label.pack(fill="x")
        self.material_menu.pack(fill="x")
        if self.material_var.get() == "Other":
            self.custom_material_entry.pack(fill="x")
        self.gauge_label.pack(fill="x")
        self.gauge_menu.pack(fill="x")
        if self.gauge_var.get() == "Other":
            self.custom_gauge_entry.pack(fill="x")
        self.status_label.pack(fill="x")
        self.status_menu.pack(fill="x")
        if status == "Reserved":
            self.project_frame.pack(fill="x")
            print("Project Name input packed below Status")
        else:
            self.project_frame.pack_forget()
            self.project_var.set("")
            print("Project Name input hidden")
        self.generate_button.pack(fill="x")
        self.save_button.pack(fill="x")
        self.generate_label()

    def upload_mill_finish(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.mill_finish_image = Image.open(file_path).resize((449, 550))
            self.generate_label()

    def draw_gradient(self, draw, x, y, width, height, colors):
        start, middle, end = colors
        for i in range(height):
            if i < height // 2:
                r = int(start[0] + (middle[0] - start[0]) * (i / (height / 2)))
                g = int(start[1] + (middle[1] - start[1]) * (i / (height / 2)))
                b = int(start[2] + (middle[2] - start[2]) * (i / (height / 2)))
            else:
                r = int(middle[0] + (end[0] - middle[0]) * ((i - height / 2) / (height / 2)))
                g = int(middle[1] + (end[1] - middle[1]) * ((i - height / 2) / (height / 2)))
                b = int(middle[2] + (end[2] - middle[2]) * ((i - height / 2) / (height / 2)))
            draw.line([(x, y + i), (x + width, y + i)], fill=(r, g, b))

    def generate_label(self):
        print("Generating label...")
        width, height = 1650, 570
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # Color block
        color = self.color_var.get()
        if color == "Other":
            custom_color = self.custom_color_entry.get() or "Unknown"
            color_text = custom_color
            hex_color = self.custom_color_value.get()
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))  # Convert hex to RGB
            draw.rectangle([0, 0, 449, 550], fill=(r, g, b))
        elif color == "Mill Finish" and self.mill_finish_image:
            image.paste(self.mill_finish_image, (0, 0))
            color_text = "Mill Finish"
        else:
            color_text = color
            if color in self.color_map:
                if self.color_map[color] == "gradient":
                    self.draw_gradient(draw, 0, 0, 449, 550, self.gradient_map[color])
                else:
                    draw.rectangle([0, 0, 449, 550], fill=self.color_map[color])
        draw.rectangle([0, 0, 449, 550], outline="black", width=5)

        # Text area with simulated bold
        material = self.material_var.get() if self.material_var.get() != "Other" else (self.custom_material_entry.get() or "Unknown")
        gauge = self.gauge_var.get() if self.gauge_var.get() != "Other" else (self.custom_gauge_entry.get() or "N/A")
        status = self.status_var.get()
        project = self.project_var.get() if status == "Reserved" else ""

        # Color title (154pt) with increased bold
        x, y = 459, 0
        for offset_x in [-2, -1, 0, 1, 2]:  # Increased offset range for more boldness
            for offset_y in [-2, -1, 0, 1, 2]:
                draw.text((x + offset_x, y + offset_y), color_text, font=self.large_font, fill="black")
        draw.line([(459, 320), (1650, 320)], fill="black", width=5)  # Lowered from 155 to 320
        # Material/gauge (100pt) moved above status block
        x, y = 459, 330  # Moved from 150 to 330
        material_text = f"{gauge} {material}".strip()
        for offset_x in [-1, 0, 1]:
            for offset_y in [-1, 0, 1]:
                draw.text((x + offset_x, y + offset_y), material_text, font=self.medium_font, fill="black")

        status_text = project if status == "Reserved" and project else status
        status_color = (95, 178, 34) if status == "Open" else (0, 99, 150)
        status_y = 440  # Kept as is
        draw.rectangle([459, status_y, 1650, status_y + 105], fill=status_color)
        draw.text((459, status_y + 5), status_text, font=self.medium_font, fill="white")
        print(f"Status block set from 459 to 1650px, y={status_y} to {status_y + 105}")

        self.current_image = image

        # Display preview
        preview_image = image.resize((825, 285), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(preview_image)
        self.preview_label.config(image=self.photo)
        print("Label generated and preview updated.")

    def save_label(self):
        if hasattr(self, "current_image"):
            self.current_image.save("label.png", "PNG", quality=100)
            print("Label saved as label.png")
        else:
            self.generate_label()
            self.save_label()

if __name__ == "__main__":
    root = tk.Tk()
    app = SheetMetalLabelGenerator(root)
    root.mainloop()