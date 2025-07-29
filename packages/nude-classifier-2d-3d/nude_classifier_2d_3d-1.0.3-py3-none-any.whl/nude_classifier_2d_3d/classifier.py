import torch
from PIL import Image
from torch import nn
from torchvision import models
from torchvision.transforms import transforms
import os

# Constants
TRANSFORMER_IMAGE_HEIGHT = 224
TRANSFORMER_IMAGE_WIDTH = 224
TRANSFORMER_NORM_MEAN = (0.485, 0.456, 0.406)
TRANSFORMER_NORM_STD = (0.229, 0.224, 0.225)
DROPOUT_PROBABILITY = 0.3
LAST_LAYER_OUT_SIZE = 1


class ClassifyNudeAs2dOr3d:
    """
    A class for binary classification of images to determine if they are real (3D) or drawn (2D) nude images.
    """

    def __init__(self, device=None, model_path=None):
        """
        Initialize the classifier with a device and model path.

        :param device: The device to run the model on ('cuda' or 'cpu'). If None, automatically selects 'cuda' if available.
        :param model_path: Path to the pre-trained model file. If None, uses the default model included in the package.
        """
        if not device:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device

        # If no model path is provided, use the package's default model
        if not model_path:
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'best_efficientnet_b0.pth')
        self.model_path = model_path

        self._create_transformer()
        self._create_model()

    def is_3d_nude_prob(self, image_path):
        """
        Calculate the probability that an image is a real (3D) nude image.

        :param image_path: Path to the input image file.
        :return: Float between 0 and 1 representing the probability of the image being a 3D nude.
        """
        image = Image.open(image_path).convert('RGB')
        image = self.transformer(image).unsqueeze(0)

        image = image.to(self.device)

        with torch.no_grad():
            outputs = self.model(image).view(-1)
            probability = torch.sigmoid(outputs).item()

        return probability

    def is_2d_nude_prob(self, image_path):
        """
        Calculate the probability that an image is a drawn (2D) nude image.

        :param image_path: Path to the input image file.
        :return: Float between 0 and 1 representing the probability of the image being a 2D nude.
        """
        return 1.0 - self.is_3d_nude_prob(image_path)

    def _create_model(self):
        self.model = models.efficientnet_b0(weights=None)
        self.model.classifier = nn.Sequential(
            nn.Dropout(DROPOUT_PROBABILITY),
            nn.Linear(self.model.classifier[1].in_features, LAST_LAYER_OUT_SIZE)
        )
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def _create_transformer(self):
        self.transformer = transforms.Compose([
            transforms.Resize((TRANSFORMER_IMAGE_HEIGHT, TRANSFORMER_IMAGE_WIDTH)),
            transforms.ToTensor(),
            transforms.Normalize(mean=TRANSFORMER_NORM_MEAN, std=TRANSFORMER_NORM_STD)
        ])