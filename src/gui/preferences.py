"""
MODULE: preferences.py
DESCRIPTION: 
Provides the UI component for managing user preferences. 
Displays previously interacted artworks (Likes and Dislikes) in a modal tabbed interface.
"""

import customtkinter as ctk
from src.gui.art_card import ArtCard

class PreferencesWindow(ctk.CTkToplevel):
    """
    A modal TopLevel window displaying the user's historical interactions.
    It blocks the main application thread to ensure context isolation while managing preferences.
    """
    def __init__(self, master, liked_artworks=None, disliked_artworks=None, **kwargs):
        super().__init__(master, **kwargs)

        self.title("Manage Preferences")
        
        # Default to empty lists if no data is provided from the DB yet
        self.liked_artworks = liked_artworks if liked_artworks is not None else []
        self.disliked_artworks = disliked_artworks if disliked_artworks is not None else []
        
        self._setup_window_size(master)
        self._setup_modality(master)
        self._setup_ui()

    def _setup_window_size(self, master):
        """ Calculates dynamic dimensions (80% of screen) and centers the modal window. """
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        modal_width = int(screen_width * 0.8)
        modal_height = int(screen_height * 0.8)
        
        pos_x = (screen_width - modal_width) // 2
        pos_y = (screen_height - modal_height) // 2
        
        self.geometry(f"{modal_width}x{modal_height}+{pos_x}+{pos_y}")

    def _setup_modality(self, master):
        """ Enforces modality. Intercepts focus to prevent background interactions. """
        self.transient(master)
        self.after(100, lambda: self.grab_set())
        self.attributes("-topmost", True)
        self.focus_force()

    def _setup_ui(self):
        """ Assembles the internal layout and initializes the scrollable grid instances. """
        self.lbl_title = ctk.CTkLabel(self, text="My Collection", font=("Roboto", 20, "bold"))
        self.lbl_title.pack(pady=10)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        self.tab_name_likes = f"My Likes {len(self.liked_artworks)}"
        self.tab_name_dislikes = f"My Dislikes {len(self.disliked_artworks)}"
        
        tab_likes = self.tabview.add(self.tab_name_likes)
        tab_dislikes = self.tabview.add(self.tab_name_dislikes)

        self.scroll_areas = {}

        # Pass the real data lists into the respective grids
        self._populate_grid(tab_likes, self.tab_name_likes, self.liked_artworks, is_liked_state=True)
        self._populate_grid(tab_dislikes, self.tab_name_dislikes, self.disliked_artworks, is_liked_state=False)

    def _populate_grid(self, parent_tab, tab_name, artworks_data, is_liked_state):
        """ Generates a 2-column scrollable grid and populates it with ArtCard components. """
        scroll_frame = ctk.CTkScrollableFrame(parent_tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)
        
        self.scroll_areas[tab_name] = scroll_frame._parent_canvas

        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=1)

        # Loop through REAL data instead of dummy range(4)
        for index, artwork in enumerate(artworks_data):
            row = index // 2
            col = index % 2
            
            # Instantiate the modular ArtCard with real backend data
            card = ArtCard(
                master=scroll_frame, 
                index=index,
                artwork_data=artwork, 
                is_liked=is_liked_state
            )
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")