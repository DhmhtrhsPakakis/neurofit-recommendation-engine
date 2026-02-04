"""
MODULE: models.py
DESCRIPTION: Converts input images into embeddings. For the clothes details using the pre-trained model resnet50.
With a preprocessing pipeline resizes images to 247 x 247 pixels. Apply normalization based on ImageNet's mean and standard deviation.
Concatenate resnet's embeddings with KMeans color vector.
"""

# --- Import Libraries ---
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image 
from utils import setup_logger
import numpy as np
from sklearn.cluster import KMeans

logger = setup_logger("Embeddings Convert")
# --- Configuration ---
imagenet_mean = [0.485, 0.456, 0.406]
imagenet_std = [0.229, 0.224, 0.225]

# --- Preprocessing Pipeline ---
image_preprocess = transforms.Compose([
    
    # 1. Resize the image. Set the smallest axe to 256 pixels
    transforms.Resize(256),

    # 2. Center Crop. Keep a 224x224 square from the center of the image
    transforms.CenterCrop(224),

    # 3. Convert to Tensor
    transforms.ToTensor(),

    # 4. Normalize based on ImageNet
    transforms.Normalize(mean=imagenet_mean, std=imagenet_std)
])


class VectorConventor:
    """
    Load the resnet model and convert the image to embeddings (vector).
    """
    def __init__(self):
        
        # Load the model.
        model = models.resnet50(weights="DEFAULT")

        # Remove the classification layer.
        self.embeddings_model = nn.Sequential(*list(model.children())[:-1])

        # evaluation mode
        self.embeddings_model.eval()


    def create_embedding(self, image_path):
        """
        Load an image from the path and convert to vector
        
        :param image_path: the path for the image
        """

        try:
            # Open the image 
            image = Image.open(image_path).convert("RGB")

            # Preprocess pipeline
            image_tensor = image_preprocess(image)   

            # Add dimension
            image_tensor_batch = image_tensor.unsqueeze(0)

            # extract the embeding
            with torch.no_grad():
                embedding = self.embeddings_model(image_tensor_batch)

            logger.info("Succesfull Embedding creation")
            return embedding.flatten().numpy()
        except FileNotFoundError:
            logger.critical(f"FIle : {image_path} does not exist.")
            raise
        

    def extract_dominant_color(self, image_path, k=1):
        """
        Extract the dominant color from the image as a normalized Vector (R,G,B) with values 0-1 using Kmeans with k=1
        
        :param image_path: the path fro the image
        :param k: the number of clusters
        """
        try:
            # Open the image
            image = Image.open(image_path).convert("RGB")

            # Crop the image to keep the clothe and resize for reduced complexity
            width, height = image.size

            # CENTER CROP
            # Keep the middle 50% of the image
            left = width * 0.25
            top = height * 0.25
            right = width * 0.75
            bottom = height * 0.75

            image = image.crop((left, top, right, bottom))
            image = image.resize((50,50))

            # Reshape / Flattening
            image_np = np.array(image)
            image_pixels = image_np.reshape(-1, 3)

            # Use K-Means
            kmeans = KMeans(n_clusters=k, n_init=10)
            kmeans.fit(image_pixels)

            # Keep the dominant color (The center of the cluster)
            dominant_color = kmeans.cluster_centers_[0]

            # Normalize from 0-255 to 0-1
            norm_dominant_color = (dominant_color/255) * 20

            logger.info("Succesfull Color Vector creation.")
            return norm_dominant_color.astype('float32')
        except FileNotFoundError:
            logger.critical(f"FIle : {image_path} does not exist.")
            raise


    def extract_image_vector(self, image_path):
        """
        Create the vector that describes the image using resnet's embeddings and KMeans color vector.
        
        :param image_path: The path for the image
        """

        # Create image embedding
        embedding = self.create_embedding(image_path)
        # Create image color vector
        color_vector = self.extract_dominant_color(image_path)

        # Concatenate to create the full vector
        return color_vector,embedding.mean(),np.concatenate([embedding,color_vector])

# --- ΔΟΚΙΜΑΣΤΙΚΟ ΤΡΕΞΙΜΟ (Αν τρέξεις αυτό το αρχείο μόνο του) ---
if __name__ == "__main__":
    # Για να το δοκιμάσεις:
    # 1. Βρες μια οποιαδήποτε εικόνα (π.χ. test.jpg) και βάλτην στον φάκελο του project.
    # 2. Άλλαξε το παρακάτω path στο όνομα της εικόνας σου.
    test_image_path = "src/mayrofoytercalvin.jpeg" 
    
    import os
    vector_convertor = VectorConventor()
    cv, emb ,vector = vector_convertor.extract_image_vector(test_image_path)
    print(f"Color Vector: {cv * 255}")
    print(f"Norm Color Vector: {cv}")
    print(f"Embedding Mean : {emb}")
    print(f"Total Vector Mean: {vector.mean()}")
    