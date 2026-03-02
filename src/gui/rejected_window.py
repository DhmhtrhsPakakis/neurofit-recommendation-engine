import customtkinter as ctk
from src.gui.art_card import ArtCard

class RejectedWindow(ctk.CTkToplevel):
    def __init__(self, master, rejected_artworks, like_callback=None, dislike_callback=None, **kwargs):
        super().__init__(master, **kwargs)

        self.title("Rejected Artworks")
        self.rejected_artworks = rejected_artworks
        self.like_callback = like_callback
        self.dislike_callback = dislike_callback
        
        self._setup_window_size(master)
        self._setup_modality(master)
        self._setup_ui()

    def _setup_window_size(self, master):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = int(sw * 0.8), int(sh * 0.8)
        x, y = (sw - w) // 2, (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_modality(self, master):
        self.transient(master)
        self.after(100, lambda: self.grab_set())
        self.attributes("-topmost", True)
        self.focus_force()

    def _setup_ui(self):
        self.lbl_title = ctk.CTkLabel(self, text="Artworks Filtered Out by AI 🤖", font=("Roboto", 20, "bold"))
        self.lbl_title.pack(pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(1, weight=1)

        if not self.rejected_artworks:
            empty_lbl = ctk.CTkLabel(self.scroll_frame, text="No artworks have been rejected yet.", text_color="gray", font=("Arial", 16))
            empty_lbl.grid(row=0, column=0, columnspan=2, pady=50)
            return

        for index, artwork in enumerate(reversed(self.rejected_artworks)):
            row = index // 2
            col = index % 2
            
            card = ArtCard(
                master=self.scroll_frame, 
                index=index,
                artwork_data=artwork, 
                is_liked=False,
                like_callback=self.like_callback,
                dislike_callback=self.dislike_callback
            )
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")