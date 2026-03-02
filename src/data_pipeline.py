import os
import json
import threading
import time
import queue
import sqlite3
from src.scraper import ArtScraper
from src.recommender import Recommender
from src.utils import setup_logger
from src.database import log_preference, add_artwork

logger = setup_logger("DataPipeline")

class DataPipeline:
    """
    Orchestrates the data flow between the Scraper, the Recommender, and the GUI.
    Runs a background thread to ensure a constant buffer of approved artworks.
    """
    def __init__(self, target_buffer_size=40, scraper_batch_size=20):
        self.target_buffer_size = target_buffer_size
        
        # Initialize our Sub-Systems
        self.scraper = ArtScraper(batch_size=scraper_batch_size)
        self.recommender = Recommender()

        # --- Queues & Buffers ---
        # A simple list for raw items (accessed only by the background thread)
        self.raw_buffer = [] 
        
        # Thread-safe queues for the GUI to consume
        # Each item will be a tuple: (artwork_dict, is_already_liked_boolean)
        self.approved_queue = queue.Queue() 
        self.rejected_queue = queue.Queue()

        self.rejected_history = []
        # Threading control
        self.is_running = False
        self.worker_thread = None

        # Memory for the User Interface
        self.cache_file = "ui_preferences.json"
        self.liked_artworks_data = []
        self.disliked_artworks_data = []
        self._load_ui_cache() # load the old artworks


    # GUI Memory management
    def _load_ui_cache(self):
        """ Loads the data for the artworks from the file for the Preferences Window """
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.liked_artworks_data = data.get("liked", [])
                self.disliked_artworks_data = data.get("disliked", [])

    def _save_ui_cache(self):
        """ Αποθηκεύει τα έργα στο αρχείο με τη μέθοδο Whitelist (Μόνο Ασφαλή Κλειδιά). """
        
        # Αυτά είναι τα ΜΟΝΑ δεδομένα (κείμενα/αριθμοί) που χρειάζεται το GUI για να ζωγραφίσει την κάρτα
        safe_keys = ['id', 'image_url', 'page_url', 'category', 'title', 'artist', 'local_path']
        
        clean_liked = []
        for art in self.liked_artworks_data:
            # Φτιάχνει ένα νέο λεξικό ΚΡΑΤΩΝΤΑΣ ΜΟΝΟ τα safe_keys
            clean_art = {k: art[k] for k in safe_keys if k in art}
            clean_liked.append(clean_art)
            
        clean_disliked = []
        for art in self.disliked_artworks_data:
            # Φτιάχνει ένα νέο λεξικό ΚΡΑΤΩΝΤΑΣ ΜΟΝΟ τα safe_keys
            clean_art = {k: art[k] for k in safe_keys if k in art}
            clean_disliked.append(clean_art)

        # Τώρα είναι ΜΑΘΗΜΑΤΙΚΑ ΑΔΥΝΑΤΟ να περάσει ndarray στο json.dump!
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump({
                "liked": clean_liked,
                "disliked": clean_disliked
            }, f)

    def start(self):
        """ Starts the background worker thread. """
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            logger.info("✅ Background Data Pipeline started.")

    def stop(self):
        """ Signals the background worker to stop. """
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join()
            logger.info("🛑 Background Data Pipeline stopped.")

    def _worker_loop(self):
        """
        The core background loop. Constantly checks if we need more approved artworks.
        If we do, it processes items from the raw_buffer or fetches new ones.
        """
        while self.is_running:
            # Check if we need to fill the approved buffer
            if self.approved_queue.qsize() < self.target_buffer_size:
                
                # 1. Do we have raw items to process? If not, fetch them!
                if not self.raw_buffer:
                    logger.info("Raw buffer empty. Fetching new batch from Scraper...")
                    new_batch = self.scraper.get_next_batch()
                    
                    if not new_batch:
                        # Scraper ran out of images or hit an error. Sleep briefly to avoid spamming.
                        time.sleep(2)
                        continue
                    
                    self.raw_buffer.extend(new_batch)

                # 2. Take the NEXT SINGLE item from the raw buffer
                candidate_artwork = self.raw_buffer.pop(0)

                # 3. Pass it through the Recommender filter
                # (We wrap it in a list because filter_artworks expects a list)
                approved, already_liked, rejected= self.recommender.filter_artworks([candidate_artwork])

                # 4. Route the result to the correct Thread-Safe Queue
                # Route to appropriate queue
                if already_liked:
                    self.approved_queue.put((already_liked[0], True))
                elif approved:
                    self.approved_queue.put((approved[0], False))
                elif rejected:
                    rej_art = rejected[0]
                    logger.warning(f"⚠️ Artwork {candidate_artwork['id']} was REJECTED (Missing Image or Filtered).")
                    self.rejected_history.append(rej_art)
                    
                    if len(self.rejected_history) > 50:
                        oldest_rejected = self.rejected_history.pop(0)
                        old_path = oldest_rejected.get('local_path')
                        import os
                        if old_path and os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                            except:
                                pass
            else:
                # Buffer is FULL (reached 40). The worker can rest for a bit.
                time.sleep(1)

    def get_gui_batch(self, count=20):
        """
        Called by the GUI to fetch the next batch of artworks.
        Returns up to 'count' items from the approved queue.
        
        Returns:
            list of tuples: [(artwork_dict, is_liked_bool), ...]
        """
        batch = []
        # Safely pull items out of the queue
        while len(batch) < count and not self.approved_queue.empty():
            batch.append(self.approved_queue.get())
        
        return batch
    

    def _save_to_db(self, ext_id, status):
        """ 
        Save the preference to the database
        """
        try:
            conn = sqlite3.connect("art_recommender.db") 
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO PREFERENCES (id, status) VALUES (?, ?)", (ext_id, status))
            conn.commit()
            conn.close()
            logger.info(f"Database Updated: {ext_id} -> {status}")
        except Exception as e:
            logger.error(f"Failed to save to DB: {e}")
        

    def _save_artwork_to_db(self, artwork_data):
        add_artwork(
            external_id=artwork_data['id'],
            image_url=artwork_data['image_url'],
            page_url=artwork_data.get('page_url', ''),
            category=artwork_data.get('category', 'Art'),
            title=artwork_data.get('title', 'Unknown'),
            artist=artwork_data.get('artist', 'Unknown'),
            embedding_vector=artwork_data['embedding_vector'])
    
    def register_like(self, artwork_data):
        """
        Triggered when the user clicks 'Like'.
        Updates the recommender's memory and (ideally) saves to the database.
        """
        ext_id = str(artwork_data['id'])
        image_url = artwork_data['image_url']
        logger.info(f"❤️ LIKED artwork: {ext_id}")
        
        self._save_artwork_to_db(artwork_data)
        # If the databse was empty and an empty list was returned
        if isinstance(self.recommender.seen_artworks, list):
            self.recommender.seen_artworks = {}
        
        # 1. Update Recommender's seen list
        self.recommender.seen_artworks[ext_id] = "LIKE"

        gui_data = artwork_data.copy()
        if 'embedding_vector' in gui_data:
            del gui_data['embedding_vector']
        
        self.liked_artworks_data.append(artwork_data)

        self._save_ui_cache()
        log_preference(image_url=image_url, preference="LIKE")
        
    def register_dislike(self, artwork_data):
        """
        Triggered when the user clicks 'Dislike'.
        Updates the recommender to avoid similar artworks.
        """
        ext_id = artwork_data['id']
        image_url = artwork_data['image_url']
        logger.info(f"👎 DISLIKED artwork: {ext_id}")
        
        self._save_artwork_to_db(artwork_data)

        # If the databse was empty and an empty list was returned
        if isinstance(self.recommender.seen_artworks, list):
            self.recommender.seen_artworks = {}

        # 1. Update Recommender's seen list
        self.recommender.seen_artworks[ext_id] = "DISLIKE"

        gui_data = artwork_data.copy()
        if 'embedding_vector' in gui_data:
            del gui_data['embedding_vector']
        
        self.disliked_artworks_data.append(artwork_data)

        self._save_ui_cache()
        log_preference(image_url=image_url, preference="DISLIKE")