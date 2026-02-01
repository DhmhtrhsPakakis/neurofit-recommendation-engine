"""
MODULE: models.py
DESCRIPTION: Converts input images into embeddings using the pre-trained model resnet50.
With a preprocessing pipeline resizes images to 247 x 247 pixels.
Apply normalization based on ImageNet's mean and standard deviation.
"""

# --- Import Libraries ---
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image 
from utils import setup_logger

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


class EmbedingConvertor:
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
        

# --- ΔΟΚΙΜΑΣΤΙΚΟ ΤΡΕΞΙΜΟ (Αν τρέξεις αυτό το αρχείο μόνο του) ---
if __name__ == "__main__":
    # Για να το δοκιμάσεις:
    # 1. Βρες μια οποιαδήποτε εικόνα (π.χ. test.jpg) και βάλτην στον φάκελο του project.
    # 2. Άλλαξε το παρακάτω path στο όνομα της εικόνας σου.
    test_image_path = "src/nohood.jpg" 
    
    import os
    embedding_convertor = EmbedingConvertor()
    vector = embedding_convertor.create_embedding(test_image_path)
    