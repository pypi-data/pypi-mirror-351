# Nude Classifier

A Python package for binary classification of images to determine if they are real (3D) or drawn (2D) nude images using a pre-trained EfficientNet-B0 model.

## Installation

### Using pip

```bash
pip install nude-classifier
```

### Using Poetry

```bash
poetry add nude-classifier
```

## Requirements
- Python 3.8+
- PyTorch
- torchvision
- PIL (Pillow)

See `requirements.txt` or `pyproject.toml` for a full list of dependencies.

## Usage

```python
from nude_classifier_2d_3d import ClassifyNudeAs2dOr3d

# Initialize the classifier
classifier = ClassifyNudeAs2dOr3d()

# Classify an image
image_path = "path/to/your/image.jpg"
prob_3d = classifier.is_3d_nude_prob(image_path)
prob_2d = classifier.is_2d_nude_prob(image_path)

print(f"Probability of 3D (real) nude: {prob_3d:.2f}")
print(f"Probability of 2D (drawn) nude: {prob_2d:.2f}")
```

## Model Details

- Architecture: EfficientNet-B0
- Input: RGB images (will be resized to 224x224 pixels)
- Output: Probability score for 3D (real) nude images
- Pre-trained Model: Included in the package (models/best_efficientnet_b0.pth)

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Disclaimer

This package is intended for research purposes only. Use responsibly and in compliance with applicable laws and regulations.


