import customtkinter as ctk
import webbrowser
from PIL import Image
import os

class ArtCard(ctk.CTkFrame):
    def __init__(self, master, index, artwork_data, is_liked=False, like_callback=None, dislike_callback=None, **kwargs):
        super().__init__(master, corner_radius=20, fg_color="#2b2b2b", **kwargs)

        self.index = index
        self.artwork_data = artwork_data
        self.is_liked = is_liked
        self.like_callback = like_callback
        self.dislike_callback = dislike_callback
        
        self.title_text = self.artwork_data.get("title", "Unknown Title")
        self.artist_text = self.artwork_data.get("artist", "Unknown Artist")
        self.page_url = self.artwork_data.get("page_url", "")
        
        # Load the local path for the image
        self.local_path = self.artwork_data.get("local_path", "") 

        self.img_size = (450, 450)
        self._setup_ui()

    def _setup_ui(self):
        # --- Load from disk ---
        if self.local_path and os.path.exists(self.local_path):
            pil_img = Image.open(self.local_path)
            self.persistent_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=self.img_size)
            
            self.img_btn = ctk.CTkButton(
                self, image=self.persistent_image, text="", 
                fg_color="transparent", hover_color="#222222",
                height=self.img_size[1], width=self.img_size[0],
                corner_radius=15, command=self._open_webpage
            )
        else:
            self.img_btn = ctk.CTkButton(
                self, text="❌ Image Missing", font=("Arial", 16),
                fg_color="#1a1a1a", hover_color="#222222",
                height=self.img_size[1], width=self.img_size[0],
                corner_radius=15, command=self._open_webpage
            )
            
        self.img_btn.pack(padx=20, pady=20, fill="x")

        # --- Meta Data ---
        display_title = (self.title_text[:40] + '...') if len(self.title_text) > 40 else self.title_text
        self.title_lbl = ctk.CTkLabel(self, text=display_title, font=("Arial", 18, "bold"))
        self.title_lbl.pack(anchor="w", padx=20)

        self.artist_lbl = ctk.CTkLabel(self, text=self.artist_text, font=("Arial", 16), text_color="gray")
        self.artist_lbl.pack(anchor="w", padx=20)

        # --- BUttons ---
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.pack(fill="x", padx=20, pady=20)

        like_bg_color = "#00FF00" if self.is_liked else "#006400"
        like_hover_color = "#00AA00" if self.is_liked else "#004d00"

        self.btn_dislike = ctk.CTkButton(
            self.actions_frame, text="DISLIKE", width=60, height=40, 
            fg_color="#8B0000", hover_color="#550000", font=("Arial", 16),
            command=self._on_dislike_click
        )
        self.btn_dislike.pack(side="left", padx=5)

        self.btn_like = ctk.CTkButton(
            self.actions_frame, text="LIKE", width=60, height=40, 
            fg_color=like_bg_color, hover_color=like_hover_color, font=("Arial", 16),
            command=self._on_like_click
        )
        self.btn_like.pack(side="left", padx=5)

        self.btn_full = ctk.CTkButton(
            self.actions_frame, text="Info", width=100, height=40, 
            fg_color="#444", hover_color="#222", command=self._open_webpage
        )
        self.btn_full.pack(side="right")

    def _on_like_click(self):
        if self.like_callback: self.like_callback(self.artwork_data)
        self.btn_like.configure(fg_color="#00FF00", hover_color="#00AA00")
        self.btn_dislike.configure(fg_color="#8B0000")

    def _on_dislike_click(self):
        if self.dislike_callback: self.dislike_callback(self.artwork_data)
        self.btn_dislike.configure(fg_color="#FF0000", hover_color="#AA0000")
        self.btn_like.configure(fg_color="#006400")

    def _open_webpage(self):
        if self.page_url: webbrowser.open(self.page_url)