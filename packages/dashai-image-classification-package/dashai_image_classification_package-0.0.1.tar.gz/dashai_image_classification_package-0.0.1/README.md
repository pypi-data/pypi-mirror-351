# Image Classification Plugin

This plugin provides the necessary tools to implement image classification tasks using the DashAI framework. The plugin includes a data loader and an MLP (Multi-Layer Perceptron) based classification model.

## Components

### ImageDataLoader
- Specialized data loader for images
- Compatible with ZIP files containing image folders
- Converts images to bytes format for processing
- Integration with HuggingFace Dataset format

### MLPImageClassifier
- Image classification model based on Multi-Layer Perceptron
- Features:
  - Configurable hidden layers
  - Adam optimizer
  - CrossEntropyLoss function
  - GPU support (CUDA)
  - Automatic image transformations (resizing to 30x30)
  - Ability to save and load trained models

## Model Parameters

- `epochs`: Number of training epochs (default: 10)
- `learning_rate`: Learning rate (default: 0.001)
- `hidden_dims`: Hidden layer dimensions (default: [128, 64])

## Requirements

- DashAI
- PyTorch
- torchvision 0.19.1

## Usage

1. Load the image dataset using `ImageDataLoader`
2. Configure the `MLPImageClassifier` model with desired parameters
3. Train the model using the `fit` method
4. Make predictions using the `predict` method

## Notes

This plugin is designed to integrate with the DashAI framework and does not implement a specific model itself, but rather provides the necessary infrastructure for image classification.