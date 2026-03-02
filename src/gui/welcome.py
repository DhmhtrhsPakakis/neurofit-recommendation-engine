import customtkinter as ctk

class WelcomeScreen(ctk.CTkFrame):
    """
    The initial landing screen of the application.
    Inherits from CTkFrame.
    """
    def __init__(self, master, start_callback, info_callback, **kwargs):
        """
        Initializes the Welcome Screen.
        
        Args:
            master: The parent window (App).
            start_callback (function): Function to run when 'Start' is clicked.
            info_callback (function): Function to run when 'How it Works' is clicked.
        """
        super().__init__(master, **kwargs)

        # 1. Title Label
        self.title_label = ctk.CTkLabel(
            self, 
            text="Welcome to Art Recommendation", 
            font=("Roboto", 24, "bold")
        )
        self.title_label.pack(pady=(80, 20)) 

        # 2. Subtitle Label
        self.sub_label = ctk.CTkLabel(
            self, 
            text="If it is your first time using the app, please read here:",
            font=("Arial", 14),
            text_color="gray"
        )
        self.sub_label.pack(pady=10)

        # 3. Info Button -> Uses info_callback
        self.info_btn = ctk.CTkButton(
            self, 
            text="How it Works", 
            command=info_callback,
            fg_color="#4a4a4a",
            hover_color="#333333",
            width=200
        )
        self.info_btn.pack(pady=10)

        # 4. Start Button -> Uses start_callback
        self.start_btn = ctk.CTkButton(
            self,
            text="Start Exploring",
            command=start_callback,
            fg_color="#009900",
            hover_color="#007700",
            width=200,
            font=("Arial", 14, "bold")
        )
        self.start_btn.pack(pady=20)