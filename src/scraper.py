"""
Provides a data provider class for the Art Institute of Chicago API.
It handles fetching public domain artworks in paginated batches, constructing
high-resolution IIIF image URLs, and generating direct links to the museum's 
website. Designed to serve as a continuous data source for the recommendation engine.
"""

import requests
from utils import setup_logger

# Logging setup
logger = setup_logger("Scraper")


class ArtScraper:
    def __init__(self, batch_size):
        """
        Initialize the Scraper.
        
        Args:
            batch_size (int): Number of images to fetch per request.
        """
        self.api_url = "https://api.artic.edu/api/v1/artworks/search"
        self.iiif_url = "https://www.artic.edu/iiif/2"
        self.website_base_url = "https://www.artic.edu/artworks" # Base URL for artwork pages
        
        self.current_page = 1
        self.batch_size = batch_size
        self.is_finished = False

    def get_next_batch(self):
        """
        Fetches the next batch of artworks.
        
        Returns:
            list: A list of dictionaries containing metadata, image URL, and page URL.
        """
        if self.is_finished:
            return []

        logger.info(f"📥 Fetching page {self.current_page}...")
        
        params = {
            "query[term][is_public_domain]": "true", # Only public domain artworks
            "fields": "id,title,image_id,artist_title,style_title",
            "limit": self.batch_size,
            "page": self.current_page
        }

        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            if response.status_code != 200:
                logger.error(f"❌ API Error: {response.status_code}")
                return []

            data = response.json()
            artworks_data = data.get('data', [])

            if not artworks_data:
                self.is_finished = True
                return []

            clean_batch = []
            for art in artworks_data:
                if not art.get('image_id'):
                    continue

                # 1. Image Link (for GUI display)
                image_id = art['image_id']
                full_image_url = f"{self.iiif_url}/{image_id}/full/843,/0/default.jpg"
                
                # 2. Page Link (for User navigation/Browser)
                # Combine base URL with artwork ID
                web_page_url = f"{self.website_base_url}/{art['id']}"

                # Category extraction (fallback to 'Art' if missing)
                category = art.get('style_title') or "Art"

                clean_batch.append({
                    "id": art['id'],
                    "image_url": full_image_url,
                    "page_url": web_page_url,
                    "category": category,
                    "title": art.get('title', 'Untitled'),
                    "artist": art.get('artist_title', 'Unknown Artist') 
                })
            self.current_page += 1
            return clean_batch

        except Exception as e:
            logger.error(f"❌ Connection Error: {e}")
            return []
