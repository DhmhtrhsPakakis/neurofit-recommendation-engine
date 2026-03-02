import customtkinter as ctk
import sys
import os

# Ensure Python can find the 'src' folder imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# --- Import our custom UI components ---
from src.gui.welcome import WelcomeScreen
from src.gui.gallery import GalleryScreen
from src.gui.preferences import PreferencesWindow
from src.data_pipeline import DataPipeline

from src.gui.rejected_window import RejectedWindow
from src.database import initialize_db

# --- Global Appearance Settings ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class ArtApp(ctk.CTk):
    """
    The Main Application Window (Orchestrator).
    Manages view transitions and global events (like scrolling).
    """
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("NeuroFit Art Recommender")
        self._setup_window_size()

        # State Variables
        self.prefs_window = None # Tracks if the preferences modal is open
        self.gallery_screen = None # Tracks the main gallery view

        # Global Scroll Bindings (Linux, Windows, macOS)
        self.bind_all("<MouseWheel>", self._on_mouse_wheel)
        self.bind_all("<Button-4>", self._on_mouse_wheel)
        self.bind_all("<Button-5>", self._on_mouse_wheel)

        initialize_db()

        # Initialize and Start the Data Pipeline
        # Download arwtosk in the background
        self.pipeline = DataPipeline(target_buffer_size=40, scraper_batch_size=20)
        self.pipeline.start()

        # Graceful Shutdown 
        # Kepp the click of the X to stop the thread
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start the Application UI
        self.show_welcome_screen()

    def _setup_window_size(self):
        """ Calculates a dynamic window size (80% of screen) and centers it. """
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        app_width = int(screen_width * 0.8)
        app_height = int(screen_height * 0.8)

        x = (screen_width - app_width) // 2
        y = (screen_height - app_height) // 2

        self.geometry(f"{app_width}x{app_height}+{x}+{y}")

    def on_closing(self):
        """ Handles the safe shutdown of background threads before closing. """
        print("System: Application termination, please wait...")
        self.pipeline.stop()  # stop the thread
        self.destroy()

    # --- VIEW ROUTING (Callbacks) ---

    def show_welcome_screen(self):
        """ Initializes and displays the Welcome Screen. """
        # Create the Welcome Screen and pass the callback functions
        self.welcome_screen = WelcomeScreen(
            master=self,
            start_callback=self.start_exploring,
            info_callback=self.open_info_panel
        )
        self.welcome_screen.pack(fill="both", expand=True, padx=20, pady=20)

    def start_exploring(self):
        """ Transitions from the Welcome Screen to the Gallery Screen. """
        # Hide the welcome screen
        self.welcome_screen.pack_forget()

        # Initialize the Gallery Screen with its callbacks
        self.gallery_screen = GalleryScreen(
            master=self,
            prefs_callback=self.open_preferences,
            next_page_callback=self.load_next_page,
            rejected_callback= self.open_rejected_window,
            pipeline = self.pipeline
        )
        self.gallery_screen.pack(fill="both", expand=True)
        
        # Load the initial batch of artworks
        self.gallery_screen.load_real_data()

    def open_info_panel(self):
        """ Opens the 'How it Works' instruction panel. """
        # We can keep this simple info modal here, or move it to a separate file later
        info_window = ctk.CTkToplevel(self)
        info_window.title("How it Works")
        
        w, h = 500, 450
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        info_window.geometry(f"{w}x{h}+{x}+{y}")
        
        info_window.transient(self)
        info_window.after(100, lambda: info_window.grab_set())
        info_window.attributes("-topmost", True)

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
   To start rejecting artworks the app must be closed and open again.

4. Rejected Artworks:
   Filtered items are moved to the 'Rejected Artworks' page.
   You can set your preference to LIKE if a artwork you like got rejected

Have fun exploring art!
        """
        text_box = ctk.CTkTextbox(info_window, font=("Arial", 14), wrap="word")
        text_box.pack(fill="both", expand=True, padx=20, pady=20)
        text_box.insert("1.0", info_text)
        text_box.configure(state="disabled")

    def open_preferences(self):
        """ Opens the Preferences Modal using the external class. """
        # Instantiate the PreferencesWindow from src.gui.preferences
        
        # Load the lists with the preferences
        liked = self.pipeline.liked_artworks_data
        disliked = self.pipeline.disliked_artworks_data 
        self.prefs_window = PreferencesWindow(master=self, liked_artworks=liked, disliked_artworks=disliked)

    def open_rejected_window(self):
        # Pipeline Record
        rejected_data = self.pipeline.rejected_history
        self.rejected_window = RejectedWindow(master=self, rejected_artworks=rejected_data, like_callback=self.pipeline.register_like, dislike_callback=self.pipeline.register_dislike)


    def load_next_page(self):
        """ Load the next page by fetching the next 20 items. """
        if self.gallery_screen:
            self.gallery_screen.load_real_data()

    
    def _on_mouse_wheel(self, event):
        """
        Routes the scroll event based on which window/tab is active.
        """
        target_canvas = None

        # 1. Check if the Preferences Modal is open and exists
        if self.prefs_window and self.prefs_window.winfo_exists():
            # Find the active tab string (e.g., "My Likes")
            active_tab = self.prefs_window.tabview.get()
            
            # Fetch the associated scroll canvas from the dictionary
            if active_tab in self.prefs_window.scroll_areas:
                target_canvas = self.prefs_window.scroll_areas[active_tab]
        
        elif hasattr(self, 'rejected_window') and self.rejected_window and self.rejected_window.winfo_exists():
            target_canvas = self.rejected_window.scroll_frame._parent_canvas
        
        # 2. Otherwise, check if the main Gallery is active
        elif self.gallery_screen and self.gallery_screen.winfo_exists():
            target_canvas = self.gallery_screen.scroll_area._parent_canvas

        # 3. Apply the scroll
        if target_canvas:
            if event.num == 4:
                target_canvas.yview_scroll(-1, "units") # Linux Up
            elif event.num == 5:
                target_canvas.yview_scroll(1, "units")  # Linux Down
            elif event.delta:
                target_canvas.yview_scroll(int(-1*(event.delta/120)), "units") # Win/Mac


# --- ENTRY POINT ---
if __name__ == "__main__":
    app = ArtApp()
    app.mainloop()