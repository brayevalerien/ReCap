import os
import tkinter as tk
from tkinter import filedialog, ttk

from PIL import Image, ImageTk

NAME = "ReCap"
VERSION = "1.0.0"


class ReCapEditor:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{NAME} v{VERSION}")
        self.root.state("zoomed")

        self.dataset_path = None
        self.image_files = []
        self.current_index = 0

        # initial screen with the Load Dataset button
        self.start_frame = ttk.Frame(root)
        self.start_frame.pack(fill=tk.BOTH, expand=True)
        load_button = ttk.Button(
            self.start_frame, text="Load Dataset", command=self.load_dataset
        )
        load_button.place(relx=.5, rely=.5, anchor="c")

        # main screen, with the image, the caption and the navigation buttons
        self.main_frame = ttk.Frame(root)

        # display image filename above the preview
        self.image_name_label = ttk.Label(self.main_frame, font=("Arial", 14))
        self.image_name_label.pack(pady=5)

        # image preview
        self.image_label = ttk.Label(self.main_frame)
        self.image_label.pack(pady=10)

        # text area for caption editing
        self.caption_text = tk.Text(
            self.main_frame, wrap=tk.WORD, height=5, font=("Arial", 12)
        )
        self.caption_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # navigation buttons (previous, next and gallery)
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.pack(pady=10)
        self.prev_button = ttk.Button(
            self.nav_frame, text="Previous", command=self.previous_image
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)
        # gallery button opens a new window showing all images in dataset, for quick navigation
        self.gallery_button = ttk.Button(
            self.nav_frame, text="Gallery", command=self.open_gallery
        )
        self.gallery_button.pack(side=tk.LEFT, padx=5)
        self.next_button = ttk.Button(
            self.nav_frame, text="Next", command=self.next_image
        )
        self.next_button.pack(side=tk.LEFT, padx=5)

    def load_dataset(self):
        self.dataset_path = filedialog.askdirectory(title="Select Dataset Folder")
        if self.dataset_path:
            self.start_frame.pack_forget()
            self.main_frame.pack(fill=tk.BOTH, expand=True)
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

        # update image name, preview and caption
        self.image_name_label.config(text=os.path.basename(image_path))
        image = Image.open(image_path)
        image.thumbnail((1600, 1000))  # Make the image larger
        self.image_tk = ImageTk.PhotoImage(image)
        self.image_label.config(image=self.image_tk)
        if os.path.exists(caption_path):
            with open(caption_path, "r", encoding="utf-8") as f:
                caption = f.read()
        else:
            caption = ""
        self.caption_text.delete(1.0, tk.END)
        self.caption_text.insert(tk.END, caption)

    def save_caption(self):
        image_path = self.image_files[self.current_index]
        caption_path = os.path.splitext(image_path)[0] + ".txt"
        caption = self.caption_text.get(1.0, tk.END).strip()
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
        """
        Open the gallery view: a new window that shows all the image in the loaded dataset, using small thumbnails. Clicking on an image will open the image in the caption editor.
        """
        self.save_caption()
        gallery_window = tk.Toplevel(self.root)
        gallery_window.title("Gallery")
        gallery_window.state("zoomed")
        canvas = tk.Canvas(gallery_window)
        scrollbar = ttk.Scrollbar(
            gallery_window, orient=tk.VERTICAL, command=canvas.yview
        )
        gallery_frame = ttk.Frame(canvas)
        gallery_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=gallery_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        thumbnail_size = 375
        for i, image_path in enumerate(self.image_files):
            image = Image.open(image_path)
            image.thumbnail((thumbnail_size, thumbnail_size))
            image_tk = ImageTk.PhotoImage(image)

            thumbnail_button = ttk.Button(
                gallery_frame,
                image=image_tk,
                command=lambda idx=i: self.select_image_from_gallery(
                    idx, gallery_window
                ),
            )
            thumbnail_button.image = image_tk  # Prevent garbage collection
            thumbnail_button.grid(row=i // 5, column=i % 5, padx=5, pady=5)

    def select_image_from_gallery(self, index, gallery_window):
        self.current_index = index
        gallery_window.destroy()
        self.load_image_and_caption()


if __name__ == "__main__":
    root = tk.Tk()
    app = ReCapEditor(root)
    root.mainloop()
