"""
Module: database.py

Description: Manages database connections and operations for storing and retrieving image embeddings.
ARTWORKS table : a table to store the artworks, which's embedding is calculated.
PREFERENCES table : Save the likes/Dislikes from the user
"""

import sqlite3
import json
import numpy as np
from datetime import datetime
from src.utils import setup_logger

logger = setup_logger("Database")

# Databse file name
DB_NAME = "art_recommender.db"

# Function to give acces to the database
def get_connection():
    return sqlite3.connect(DB_NAME)

def initialize_db():
    """
    Create the tables. 
    """                                                                                     

    conn = get_connection()
    cursor = conn.cursor()

    # --- Artworks Table ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ARTWORKS(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   external_id INTEGER UNIQUE, -- the id from the museum API
                   image_url TEXT UNIQUE,
                   page_url TEXT,
                   category TEXT,
                   title TEXT,
                   artist TEXT,
                   embedding TEXT, -- save as json string
                   created_at TIMESTAMP
                )
        ''')
    
    # --- Interaction Table ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PREFERENCES(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   artwork_id INTEGER UNIQUE,
                   preference TEXT, -- "LIKE" or "DISLIKE"
                   timestamp TIMESTAMP,
                   FOREIGN KEY(artwork_id) REFERENCES ARTWORKS(id) 
                   )
        ''')
    
    conn.commit()
    conn.close()
    logger.info("Database Tables succesfully created.")


# --- ADD Artwork ---
def add_artwork(external_id: int, image_url : str, page_url : str , category : str, title : str, artist : str, embedding_vector : np.ndarray) -> None:
    """
    Add a new artwork with it's embedding to the ARTWORKS table
    
    :param external_id: the id for each artwork from the museum's API
    :type external_id: int
    :param image_url: the url for the image
    :type url: str
    :param page_url: the url for the site's page
    :type page_url: str
    :param category: artwork;s category
    :type category: str
    :param title: artwork title
    :type title: str
    :param artist: the artwork's artist
    :type artist: str
    :param embedding_vector: Image's embedding from resnet50
    :type embedding_vector: np.ndarray

    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO ARTWORKS (external_id, image_url, page_url, category, title, artist, embedding, created_at)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                       ''',(external_id, image_url, page_url, category, title, artist, json.dumps(embedding_vector.tolist()), datetime.now()))
        conn.commit()
    except sqlite3.IntegrityError:
        logger.warning(f"The artwork {image_url} already exists in the database. Unsuccesfully insert.")
    finally:
        conn.close()

# --- ADD/EDIT PREFERENCE ---
def log_preference(image_url : str , preference : str) -> None:
    """
    Add or edit a preference of the user for an artwork
    
    :param image_url: the url of the image
    :type url: str
    :param preference: LIKE OR DISLIKE
    :type preference: str
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Find the artwork's id from the url
    cursor.execute("SELECT id FROM ARTWORKS WHERE image_url = ?", (image_url,))
    result = cursor.fetchone()

    if result:
        artwork_id = result[0]
        cursor.execute('''
            INSERT OR REPLACE INTO PREFERENCES (artwork_id, preference, timestamp)
            VALUES(?, ?, ?)
                       ''', (artwork_id, preference, datetime.now()))
        
        conn.commit()
        logger.info(f"The preference for the artwork {artwork_id} is set to {preference}.")
    else:
        logger.error("The artwork was not found in the database.")

    conn.close()

#--- Remove user's preference for a product
def remove_preference(url: str) -> None :
    """
    Remove the users preference for an artwork.
    
    :param url: the url of the artwork
    :type url: str
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Find the artwork's id using the url
    cursor.execute("SELECT id FROM ARTWORKS WHERE image_url = ?", (url,))
    result = cursor.fetchone()[0]

    # If the remove_preference function is called then the product is surely in the table
    cursor.execute(" DELETE FROM PREFERENCES WHERE artwork_id = ?", (result,))
    conn.commit()
    logger.info(f"The preference for the artwork {result} was succesfully removed.")

    conn.close()

#--- Get the artworks and their preference as dictionary ---
def user_preferences_dict() -> dict:
    """
    Find the artworks the user has a preference and save to a a dictionary ({external_id : "Preference"})
    
    :return: A dictionary with the artowrk id and user preference
    :rtype: dict
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT A.external_id, P.preference FROM PREFERENCES P JOIN ARTWORKS A ON P.artwork_id=A.id
                   ''')
    
    rows = cursor.fetchall()
    preferences_dict = {row[0]: row[1] for row in rows}

    conn.close()

    return [preferences_dict]


#--- Get the users embeddings for the artworks
def user_embeddings() -> tuple:
    """
    Find the images that the user likes and return the embeddings
    
    :return: LikedEmbeddings, DislikedEmbeddings
    :rtype: tuple
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Fetch LIKES
    cursor.execute('''
        SELECT A.embedding FROM ARTWORKS A JOIN PREFERENCES PREF ON A.id = PREF.artwork_id  WHERE PREF.preference = "LIKE" ''')
    liked = [np.array(json.loads(row[0])) for row in cursor.fetchall() if row[0]]

    # Fetch DISLIKES
    cursor.execute('''
        SELECT A.embedding FROM ARTWORKS A JOIN PREFERENCES PREF ON A.id = PREF.artwork_id  WHERE PREF.preference = "DISLIKE" ''')
    disliked = [np.array(json.loads(row[0])) for row in cursor.fetchall() if row[0]]
    
    conn.close()
    return liked, disliked

if __name__ == "__main__":
    initialize_db()