"""
MODULE: recommender.py
DESCRIPTION: Implements a Content-Based Visual Recommendation Engine using ResNet50 embeddings.
It orchestrates the data flow between the ArtScraper (Data Source) and the Database (User Profile).
The architecture utilizes **In-Memory Caching** (O(1) lookups) to efficiently handle existing user preferences.
For new candidates, it calculates the Cosine Similarity against the user's positive interactions.
Items are filtered based on a similarity threshold (e.g., >0.30), while previously interacted items are preserved to maintain user context.
"""

import os
import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils import setup_logger
from database import user_embeddings, user_preferences_dict
from model import VectorConverter

logger = setup_logger("Recommender")

class Recommender:
    def __init__(self):

        self.converter = VectorConverter()

        # The similarity threshold 
        self.similarity_threshold = 0.30

        # Load the artworks the user has seen and has a preference
        self.seen_artworks = user_preferences_dict()

        # Load the user's preferences
        self.liked_embeddings, self.disliked_embeddings = user_embeddings()

        logger.info(f"Recommender is set. Memory Loaded: {len(self.seen_artworks)} interactions")


    def _download_image(self, url, filename):
            """
            Downloads an imagte to a temporary file            
            """
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                r = requests.get(url, headers=headers, stream=True, timeout=10)
                if r.status_code == 200:
                    with open(filename, 'wb') as f:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)
                    return True
            except:
                return False
            return False
        
    def similarity_check(self, candidate_vector):
         """
         Check if the artowrk pass the similarity test.
         If the artowrk has a similarity over 0.30 with one artwork at least in preferences then it pass.
         """
        
         # if the user does not have more than 5 likes then the artwork pass
         if len(self.liked_embeddings) < 5:
              return True
         
         candidate_vector = candidate_vector.reshape(1, -1)
         liked_embeddings = np.array(self.liked_embeddings)
         disliked_embeddings = np.array(self.disliked_embeddings)

         for dis_emb in disliked_embeddings:
              dis_emb = dis_emb.reshape(1, -1)
              cos_similarity = cosine_similarity(candidate_vector, dis_emb)[0][0]
              if cos_similarity > 0.7 :
                   return False
    
         for emb in liked_embeddings:
              emb = emb.reshape(1, -1)
              cos_similarity = cosine_similarity(candidate_vector, emb)
              if cos_similarity > 0.3 :
                   return True
         return False
    
    def filter_artworks(self, artworks):
         """
         Check every artwork from the scraper's batch if passes the similarity check. Return only the passed artworks.
         """
        
         approved_artworks = []
         already_approved_artworks = []
         temp_filename  = "temp.jpg"

         for artwork in artworks:
              ext_id = artwork['id']

              # Check if the artwork is in the preference list
              if ext_id in self.seen_artworks:
                   if not self.seen_artworks[ext_id] == "DISLIKE":
                        already_approved_artworks.append(artwork)
                   continue
              
              if self._download_image(artwork['image_url'], temp_filename):
                   try:
                        # Create the embedding
                        vector = self.converter.create_embedding(temp_filename)

                        # Check if the image pass the similarity check
                        passes = self.similarity_check(vector)

                        if passes == True:
                             approved_artworks.append(artwork)
                   except Exception as e:
                        logger.error(f"Error checking artwork {ext_id}: {e}")

         # Delete temporary image file
         if os.path.exists(temp_filename):
              os.remove(temp_filename)
        
         return approved_artworks, already_approved_artworks