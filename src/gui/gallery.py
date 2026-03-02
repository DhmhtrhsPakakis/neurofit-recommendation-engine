import customtkinter as ctk
from src.gui.art_card import ArtCard

class GalleryScreen(ctk.CTkFrame):
    def __init__(self, master, prefs_callback, next_page_callback, rejected_callback, pipeline, **kwargs):
        super().__init__(master, **kwargs)

        self.pipeline = pipeline
        self.items_per_page = 20
        self.rendered_cards = [] 

        self.header_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=10)

        self.gallery_title = ctk.CTkLabel(self.header_frame, text="Your Art Feed", font=("Roboto", 20, "bold"))
        self.gallery_title.pack(side="left")

        btn_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_container.pack(side="right")

        self.prefs_btn = ctk.CTkButton(btn_container, text="See Preferences", command=prefs_callback, fg_color="#333333", hover_color="#555555", width=140)
        self.prefs_btn.pack(side="left", padx=10)

        self.rejected_btn = ctk.CTkButton(
            btn_container, text="Rejected Artworks", width=120, 
            fg_color="#555555", hover_color="#333333", 
            command=rejected_callback
        )

        self.scroll_area = ctk.CTkScrollableFrame(self, label_text="Page 1")
        self.scroll_area.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.scroll_area.grid_columnconfigure(0, weight=1) 
        self.scroll_area.grid_columnconfigure(1, weight=1) 

        self.loading_label = ctk.CTkLabel(
            self.scroll_area, 
            text="Curating your personalized gallery...\nPlease wait.", 
            font=("Arial", 18, "bold"),
            text_color="gray"
        )

        self.footer_frame = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.footer_frame.pack(fill="x", pady=10)

        self.next_page_btn = ctk.CTkButton(self.footer_frame, text="Next Page", width=200, height=40, font=("Arial", 16, "bold"), command=next_page_callback)
        self.next_page_btn.pack(pady=5)

        self.rejected_btn.pack(side = "left")
        

    def _clear_grid(self):
        for card in self.rendered_cards:
            try:
                card.destroy()
            except:
                pass
        self.rendered_cards.clear()

    def load_real_data(self):
        ready_count = self.pipeline.approved_queue.qsize()

        if ready_count < self.items_per_page:
            self._clear_grid() # CLean only if we are at the beggining
            self.next_page_btn.configure(state="disabled") 
            self.loading_label.grid(row=0, column=0, columnspan=2, pady=50)
            self.after(500, self.load_real_data)
            return

        print("[UI] Building cards on screen...")
        self.loading_label.grid_forget() 
        self.next_page_btn.configure(state="normal") 

        batch = self.pipeline.get_gui_batch(self.items_per_page)

        for index, (artwork_data, is_liked) in enumerate(batch):
            row = index // 2 
            col = index % 2
            
            card = ArtCard(
                master=self.scroll_area, 
                index=index,
                artwork_data=artwork_data,
                is_liked=is_liked,
                like_callback=self.pipeline.register_like,
                dislike_callback=self.pipeline.register_dislike
            )
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            self.rendered_cards.append(card) # Save to the list
            
        print("[UI] Cards placed. Forcing Screen Update...")
        self.update_idletasks()
        self.scroll_area._parent_canvas.yview_moveto(0)