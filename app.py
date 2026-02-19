import customtkinter as ctk

# --- APPEARANCE SETTINGS ---
ctk.set_appearance_mode("Dark")  # Sets the app to Dark Mode
ctk.set_default_color_theme("dark-blue")  # Sets the color theme for buttons

class ArtApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. WINDOW SETUP
        self.title("Art Recommendation App")
        
        # Define window dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = int(screen_width*0.8)
        window_height = int(screen_height*0.8)

        # --- SCROLL FIX (Linux & Windows) ---
        # Windows/MacOS use <MouseWheel>
        self.bind_all("<MouseWheel>", self._on_mouse_wheel)
        
        # Linux uses Button-4 (Up) and Button-5 (Down)
        self.bind_all("<Button-4>", self._on_mouse_wheel)
        self.bind_all("<Button-5>", self._on_mouse_wheel)

        # Center the window on the screen
        self.center_window(self, window_width, window_height)

        # 2. WELCOME FRAME (Container)
        # Create a frame to hold the welcome elements
        self.welcome_frame = ctk.CTkFrame(self)
        self.welcome_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 3. TITLE LABEL
        self.title_label = ctk.CTkLabel(
            self.welcome_frame, 
            text="Welcome to Art Recommendation", 
            font=("Roboto", 24, "bold")
        )
        # Add padding at the top to push it down slightly
        self.title_label.pack(pady=(80, 20)) 

        # 4. SUBTITLE / INSTRUCTION LABEL
        self.sub_label = ctk.CTkLabel(
            self.welcome_frame, 
            text="If it is your first time using the app, please read here:",
            font=("Arial", 14),
            text_color="gray"
        )
        self.sub_label.pack(pady=10)

        # 5. INFO BUTTON
        # Clicking this calls the 'open_info_panel' method
        self.info_btn = ctk.CTkButton(
            self.welcome_frame, 
            text="How it Works", 
            command=self.open_info_panel,
            fg_color="#4a4a4a", # Custom gray color
            hover_color="#333333", # Darker gray on hover
            width=200
        )
        self.info_btn.pack(pady=10)

        # 6. START BUTTON (Placeholder for next step)
        self.start_btn = ctk.CTkButton(
            self.welcome_frame,
            text="Start Exploring",
            command=self.start_exploring,
            fg_color="#009900", # Green color
            hover_color="#007700",
            width=200,
            font=("Arial", 14, "bold")
        )
        self.start_btn.pack(pady=20)

    def _find_scrollable_parent(self, widget):
        """
        Helper Function: Recursively walks up the widget hierarchy 
        to find a scrollable 'Canvas' widget.
        """
        current = widget
        # Walk up the widget tree (max 10 levels to prevent infinite loops)
        for _ in range(10):
            if not current:
                break
            
            # Check if the widget is a Canvas (which CTkScrollableFrame uses internally)
            # We check if it supports the 'yview_scroll' method.
            if hasattr(current, 'yview_scroll') and current.winfo_class() == 'Canvas':
                return current
            
            # Go to the parent widget
            current = current.master
        return None

    def _on_mouse_wheel(self, event):
        """ 
        Context-Aware Scroll Handler.
        Identifies WHICH widget is under the mouse and scrolls ONLY that one.
        """
        # 1. Get the widget strictly under the mouse pointer
        x_root = self.winfo_pointerx()
        y_root = self.winfo_pointery()
        target_widget = self.winfo_containing(x_root, y_root)

        # 2. Find if this widget lives inside a scrollable area
        scrollable_canvas = self._find_scrollable_parent(target_widget)

        # 3. If a valid scrollable area is found, apply the scroll event
        if scrollable_canvas:
            # Linux Logic (Button 4/5)
            if event.num == 4:
                scrollable_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                scrollable_canvas.yview_scroll(1, "units")
            
            # Windows/Mac Logic (Delta)
            elif event.delta:
                 scrollable_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                
    def center_window(self, window_object, width, height):
        """
        Calculates the x, y coordinates to center the window on the screen.
        """
        # Get the screen dimension
        screen_width = window_object.winfo_screenwidth()
        screen_height = window_object.winfo_screenheight()

        # Find the center point
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set the geometry (Width x Height + X_pos + Y_pos)
        window_object.geometry(f"{width}x{height}+{x}+{y}")

    def open_info_panel(self):
        """
        Opens a new Toplevel window (popup) with instructions.
        """
        # Create a secondary window on top of the main one
        info_window = ctk.CTkToplevel(self)
        info_window.title("How it Works")

        # Make it modal
        info_window.after(100, lambda: info_window.grab_set())
        
        # Center this new window too (slightly smaller)
        self.center_window(info_window, 500, 450)
        
        # Keep it on top of other windows
        info_window.attributes("-topmost", True)

        # Instruction Text
        info_text = """
Welcome User!

Here is how the Art Recommendation App works:

1. View Artworks:
   -You will be presented with various paintings.
   -Click the image to visit the museum's page.
   -Click 'Open Full' to see the high-res image.

2. Rate Artworks:
   -LIKE: If you enjoy the artwork.
   -DISLIKE: If it's not your style.

3. Personalization:
   Once you gather 5 likes, the system starts learning!
   It will automatically hide artworks similar to your Dislikes.

4. Rejected Artworks:
   Filtered items are moved to the 'Rejected Artworks' page.

Have fun exploring art!
        """

        # Text Box to display the info
        text_box = ctk.CTkTextbox(info_window, font=("Arial", 14), wrap="word")
        text_box.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Insert text and make it read-only
        text_box.insert("1.0", info_text)
        text_box.configure(state="disabled")


    def start_exploring(self):
        """
        Transition function: Hides the Welcome Screen and builds the Gallery UI.
        """
        # 1. Hide the Welcome Frame
        # The pack_forget() method removes the widget from the window but keeps it in memory.
        self.welcome_frame.pack_forget()

        # 2. Build the Gallery Interface
        self.setup_gallery_ui()
        
        # 3. Load dummy data (Just for visual testing right now)
        self.load_dummy_data()


    def setup_gallery_ui(self):
        """
        Sets up the main structure of the Gallery View:
        - Header (Title + Filters)
        - Scrollable Area (For artworks)
        - Footer (Pagination controls)
        """
        
        # --- A. MAIN CONTAINER ---
        # A frame that holds everything for the gallery view
        self.gallery_frame = ctk.CTkFrame(self)
        self.gallery_frame.pack(fill="both", expand=True)

        # --- B. HEADER ---
        self.header_frame = ctk.CTkFrame(self.gallery_frame, height=50, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=10)

        # Title
        self.gallery_title = ctk.CTkLabel(
            self.header_frame, 
            text="Your Art Feed", 
            font=("Roboto", 20, "bold")
        )
        self.gallery_title.pack(side="left")

        # Buttons Container
        btn_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_container.pack(side="right")

        self.prefs_btn = ctk.CTkButton(btn_container, text="See Preferences", command=self.open_preferences,
                                       fg_color="#333333", hover_color="#555555", width=140)
        self.prefs_btn.pack(side="left", padx=10)

        self.rejected_btn = ctk.CTkButton(btn_container, text="Rejected Artworks", width=120, fg_color="#555555", hover_color="#333333")
        self.rejected_btn.pack(side="left")

        # --- C. SCROLLABLE AREA (The Core) ---
        # CTkScrollableFrame handles the scrollbar automatically!
        self.scroll_area = ctk.CTkScrollableFrame(self.gallery_frame, label_text="Page 1")
        self.scroll_area.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Grid Configuration: We want 2 equal columns
        # weight=1 means "expand to fill available space"
        self.scroll_area.grid_columnconfigure(0, weight=1) # Column 0
        self.scroll_area.grid_columnconfigure(1, weight=1) # Column 1

        # --- D. FOOTER (Pagination) ---
        self.footer_frame = ctk.CTkFrame(self.gallery_frame, height=60, fg_color="transparent")
        self.footer_frame.pack(fill="x", pady=10)

        self.next_page_btn = ctk.CTkButton(
            self.footer_frame,
            text="Next Page",
            width=200,
            height=40,
            font=("Arial", 16, "bold"),
            command=self.load_next_page # Will define this logic later
        )
        self.next_page_btn.pack(pady=5)

    def load_dummy_data(self):
        """
        Temporary function to populate the grid with placeholders.
        Simulates 20 artworks.
        """
        for i in range(20):
            # Calculate Grid Position (2 Columns)
            # Example: i=0 -> row=0, col=0 | i=1 -> row=0, col=1 | i=2 -> row=1, col=0
            row = i // 2 
            col = i % 2
            
            self.create_art_card(self.scroll_area, i, row, col)   

    def create_art_card(self, parent_widget, index, row, col, info_tag=""):
        """ 
        GENERIC Function to create an Art Card.
        Args:
            parent_widget: Where to put the card (Main Gallery OR Preferences Tab)
            index: ID number
            row, col: Grid position
            info_tag: Extra text (e.g., "(Liked)")
        """
        
        # 1. Main Card Frame
        card = ctk.CTkFrame(parent_widget, corner_radius=20, fg_color="#2b2b2b")
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

        # 2. Image Placeholder (BIG & SQUARE)
        img_btn = ctk.CTkButton(
            card,
            text=f"🖼️\n\nImage {index+1}\n(450x450)", 
            font=("Arial", 20),
            fg_color="#1a1a1a",
            hover_color="#222222",
            height=450, 
            width=450,
            corner_radius=15
        )
        img_btn.pack(padx=20, pady=20, fill="x")

        # 3. Info Section
        title_text = f"Artwork #{index + 1} {info_tag}"
        title_lbl = ctk.CTkLabel(card, text=title_text, font=("Arial", 18, "bold"))
        title_lbl.pack(anchor="w", padx=20)

        artist_lbl = ctk.CTkLabel(card, text="Famous Artist Name", font=("Arial", 16), text_color="gray")
        artist_lbl.pack(anchor="w", padx=20)

        # 4. Buttons Row
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=20)

        btn_dislike = ctk.CTkButton(actions_frame, text="👎", width=60, height=40, fg_color="#8B0000", hover_color="#550000", font=("Arial", 16))
        btn_dislike.pack(side="left", padx=5)

        btn_like = ctk.CTkButton(actions_frame, text="👍", width=60, height=40, fg_color="#006400", hover_color="#004d00", font=("Arial", 16))
        btn_like.pack(side="left", padx=5)

        btn_full = ctk.CTkButton(actions_frame, text="🔍 View Full", width=100, height=40, fg_color="#444", hover_color="#222")
        btn_full.pack(side="right")

    def load_dummy_data(self):
        """ Populates the MAIN gallery """
        for i in range(10): 
            row = i // 2 
            col = i % 2
            # Pass self.scroll_area as the parent
            self.create_art_card(self.scroll_area, i, row, col)

    # --- PREFERENCES WINDOW (UPDATED) ---

    def open_preferences(self):
        """ Opens a Modal Window that looks like a Gallery """
        prefs_window = ctk.CTkToplevel(self)
        prefs_window.title("Manage Preferences")
        
        # Make it BIG (same logic as main window but slightly smaller)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w, h = int(sw * 0.8), int(sh * 0.8)
        x, y = (sw - w) // 2, (sh - h) // 2
        prefs_window.geometry(f"{w}x{h}+{x}+{y}")
        
        prefs_window.after(100, lambda: prefs_window.grab_set())
        prefs_window.attributes("-topmost", True)
        prefs_window.focus()

        # --- MODAL LOGIC START ---
        # 1. Transient: Tells OS this window is a dialog of the main app
        prefs_window.transient(self)
        
        # 2. Grab Set: Blocks events to the main window
        # We wait 100ms to ensure the window is fully registered by the OS
        prefs_window.after(100, lambda: prefs_window.grab_set())
        
        # 3. Focus: Bring keyboard focus here
        prefs_window.focus_force()
        
        # 4. On Top: Keep it visually above
        prefs_window.attributes("-topmost", True)
        # --- MODAL LOGIC END ---
        lbl = ctk.CTkLabel(prefs_window, text="My Collection", font=("Roboto", 20, "bold"))
        lbl.pack(pady=10)

        # Tabs
        tabview = ctk.CTkTabview(prefs_window)
        tabview.pack(fill="both", expand=True, padx=20, pady=10)

        tab_likes = tabview.add("My Likes")
        tab_dislikes = tabview.add("My Dislikes")

        # Fill Tabs with GRID layout
        self.populate_prefs_grid(tab_likes, tag="(Liked)")
        self.populate_prefs_grid(tab_dislikes, tag="(Disliked)")

    def populate_prefs_grid(self, parent_tab, tag):
        """ 
        Creates a Grid Gallery INSIDE a Tab using create_art_card.
        """
        # 1. Create a Scrollable Frame for the Tab
        scroll_frame = ctk.CTkScrollableFrame(parent_tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)
        
        # 2. Configure Grid (2 Columns)
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=1)

        # 3. Add Dummy Cards (e.g., 4 items)
        for i in range(4):
            row = i // 2
            col = i % 2
            # REUSE the same function! Pass scroll_frame as parent.
            self.create_art_card(scroll_frame, i, row, col, info_tag=tag)
        
    def load_next_page(self):
        print("Loading next page logic...") # Placeholder logic

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    app = ArtApp()
    app.mainloop()