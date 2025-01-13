import os
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image

NAME = "ReCap"
VERSION = "1.1.0"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("themes/lavender.json")  # from CTkThemesPack


class ReCapEditor:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{NAME} v{VERSION}")
        self.root.state("normal")
        self.root.state("zoomed")

        self.dataset_path = None
        self.image_files = []
        self.current_index = 0

        # Initial screen with Load Dataset button
        self.start_frame = ctk.CTkFrame(root)
        self.start_frame.pack(fill="both", expand=True)
        load_button = ctk.CTkButton(
            self.start_frame,
            text="Load Dataset",
            command=self.load_dataset,
            font=("Arial", 16),
        )
        load_button.place(relx=0.5, rely=0.5, anchor="center")

        # Main screen components
        self.main_frame = ctk.CTkFrame(root)

        # Image filename display
        self.image_name_label = ctk.CTkLabel(self.main_frame, font=("Arial", 14))
        self.image_name_label.pack(pady=5)

        # Image preview
        self.image_label = ctk.CTkLabel(self.main_frame, text="", anchor="center")
        self.image_label.pack(pady=10)

        # Text area for caption editing
        self.caption_text = ctk.CTkTextbox(
            self.main_frame, wrap="word", height=150, font=("Arial", 12)
        )
        self.caption_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Navigation buttons (previous, gallery, next)
        self.nav_frame = ctk.CTkFrame(self.main_frame)
        self.nav_frame.pack(pady=10)

        self.prev_button = ctk.CTkButton(
            self.nav_frame, text="Previous", command=self.previous_image
        )
        self.prev_button.pack(side="left", padx=5)

        self.gallery_button = ctk.CTkButton(
            self.nav_frame, text="Gallery", command=self.open_gallery
        )
        self.gallery_button.pack(side="left", padx=5)

        self.next_button = ctk.CTkButton(
            self.nav_frame, text="Next", command=self.next_image
        )
        self.next_button.pack(side="left", padx=5)

    def load_dataset(self):
        self.dataset_path = filedialog.askdirectory(title="Select Dataset Folder")
        if self.dataset_path:
            self.start_frame.pack_forget()
            self.main_frame.pack(fill="both", expand=True)
            self.load_images()
            if self.image_files:
                self.load_image_and_caption()

    def load_images(self):
        for root, _, files in os.walk(self.dataset_path):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg")):
                    self.image_files.append(os.path.join(root, file))

    def load_image_and_caption(self):
        image_path = self.image_files[self.current_index]
        caption_path = os.path.splitext(image_path)[0] + ".txt"

        # Update image name, preview, and caption
        self.image_name_label.configure(text=os.path.basename(image_path))
        image = Image.open(image_path)
        # image.thumbnail((1000, 1000))
        self.image_ctk = ctk.CTkImage(image, size=(768, 768))
        self.image_label.configure(image=self.image_ctk, text="")

        if os.path.exists(caption_path):
            with open(caption_path, "r", encoding="utf-8") as f:
                caption = f.read()
        else:
            caption = ""

        self.caption_text.delete("1.0", "end")
        self.caption_text.insert("end", caption)

    def save_caption(self):
        image_path = self.image_files[self.current_index]
        caption_path = os.path.splitext(image_path)[0] + ".txt"
        caption = self.caption_text.get("1.0", "end").strip()
        with open(caption_path, "w", encoding="utf-8") as f:
            f.write(caption)

    def next_image(self):
        self.save_caption()
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_image_and_caption()

    def previous_image(self):
        self.save_caption()
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image_and_caption()

    def open_gallery(self):
        self.save_caption()
        gallery_window = ctk.CTkToplevel(self.root)
        gallery_window.title("Gallery")
        gallery_window.geometry("1200x800")

        canvas = ctk.CTkCanvas(gallery_window)
        scrollbar = ctk.CTkScrollbar(
            gallery_window, orientation="vertical", command=canvas.yview
        )
        gallery_frame = ctk.CTkFrame(canvas)
        gallery_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=gallery_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        thumbnail_size = 375
        for i, image_path in enumerate(self.image_files):
            image = Image.open(image_path)
            image.thumbnail((thumbnail_size, thumbnail_size))
            image_ctk = ctk.CTkImage(image, size=(thumbnail_size, thumbnail_size))

            thumbnail_button = ctk.CTkButton(
                gallery_frame,
                image=image_ctk,
                command=lambda idx=i: self.select_image_from_gallery(
                    idx, gallery_window
                ),
                text="",
            )
            thumbnail_button.image = image_ctk  # Prevent garbage collection
            thumbnail_button.grid(row=i // 5, column=i % 5, padx=5, pady=5)

    def select_image_from_gallery(self, index, gallery_window):
        self.current_index = index
        gallery_window.destroy()
        self.load_image_and_caption()


if __name__ == "__main__":
    root = ctk.CTk()
    app = ReCapEditor(root)
    root.mainloop()
