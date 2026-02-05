"""
Module: database.py

Description: Manages database connections and operations for storing and retrieving image embeddings.
Product table : a table to store the products, which's embedding is calculated.
Interaction table : Save the likes/Dislikes from the user
"""

import sqlite3
import json
import numpy as np
from datetime import datetime
from utils import setup_logger

logger = setup_logger("Database")

# Databse file name
DB_NAME = "neurofit.db"

# Function to give acces to the database
def get_connection():
    return sqlite3.connect(DB_NAME)

def initialize_db():
    """
    Create the tables. 
    """

    conn = get_connection()
    cursor = conn.cursor()

    # --- Products Table ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PRODUCTS(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   url TEXT UNIQUE,
                   image_path TEXT,
                   category TEXT,
                   embedding TEXT, -- save as json string
                   created_at TIMESTAMP
                )
        ''')
    
    # --- Interaction Table ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PREFERENCES(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   product_id INTEGER,
                   preference TEXT, -- "LIKE" or "DISLIKE"
                   timestamp TIMESTAMP,
                   FOREIGN KEY(product_id) REFERENCES PRODUCTS(id)
                   CONSTRAINT unique_product UNIQUE(product_id) 
                   )
        ''')
    
    conn.commit()
    conn.close()
    logger.info("Database Tables succesfully created.")


# --- ADD PRODUCT ---
def add_product(url : str, image_path : str , embedding_vector : np.ndarray, category : str) -> None:
    """
    Add a new product with it's embedding to the PRODUCTS table
    
    :param url: the url of the product
    :type url: str
    :param image_path: the path for the product's image
    :type image_path: str
    :param embedding_vector: Image's embedding from resnet50
    :type embedding_vector: np.ndarray
    :param category: clothe's category
    :type embedding_vector: str
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO PRODUCTS (url, image_path, embedding, created_at)
            VALUES(?, ?, ?, ?, ?)
                       ''',(url, image_path, category, json.dumps(embedding_vector.tolist()), datetime.now()))
        conn.commit()
    except sqlite3.IntegrityError:
        logger.warning(f"The product {url} already exists in the database. Unsuccesfully insert.")
    finally:
        conn.close()

# --- ADD/EDIT PREFERENCE ---
def log_preference(url : str , preference : str) -> None:
    """
    Add or edit a preference of the user for a product
    
    :param url: the url of the product
    :type url: str
    :param preference: LIKE OR DISLIKE
    :type preference: str
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Find the product's id from the url
    cursor.execute("SELECT id FROM PRODUCTS WHERE url = ?", (url,))
    result = cursor.fetchone()

    if result:
        product_id = result[0]
        cursor.execute('''
            INSERT OR REPLACE INTO PREFERENCES (id, product_id, preference, timestamp)
            VALUES(
                    (SELECT id FROM PREFERENCES WHERE product_id = ?), ?, ?, ?)
                       ''', (product_id, product_id, preference, datetime.now()))
        
        conn.commit()
        logger.info(f"The preference for the product {product_id} is set to {preference}.")
    else:
        logger.error("The product was not found in the database.")

    conn.close()

#--- Remove user's preference for a product
def remove_preference(url: str) -> None :
    """
    Remove the users preference for a product.
    
    :param url: the url of the product
    :type url: str
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Find the product's id using the url
    cursor.execute("SELECT id FROM PRODUCTS WHERE url = ?", (url,))
    result = cursor.fetchone()

    # If the remove_preference function is called then the product is surely in the table
    cursor.execute(" DELETE FROM PREFERENCES WHERE product_id = ?", (result,))
    conn.commit()
    logger.info(f"The preference for the product {result} was succesfully removed.")

    conn.close()

#--- Get the users embeddings for the LIKE products
def user_liked_embeddings(category : str) -> np.ndarray:
    """
    Find the images that the user likes and return the embeddings
    
    :param category: clothe's category
    :type category: str
    :return: embeddings
    :rtype: ndarray[2048, dtype[float]]
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT P.embedding FROM PRODUCTS P JOIN PREFERENCES PREF ON P.id = PREF.product_id  WHERE PREF.preference = "LIKE" AND P.category = ?
                  ''', (category,))
    
    embeddings = []
    for embedding in cursor.fetchall():
        vector = np.array(json.loads(embedding[0]))
        embeddings.append(vector)
    
    conn.close()
    return embeddings


if __name__ == "__main__":
    initialize_db()