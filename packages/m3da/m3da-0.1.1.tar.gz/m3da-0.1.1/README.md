# M3da

A lightweight Python package for image classification using ONNX models.

## Installation

```bash
pip install m3da
```

## Features

- Simple interface for image classification using ONNX models
- Automatic image preprocessing and normalization
- Input validation to prevent common errors
- Compatible with any ONNX model trained for image classification

## Requirements

- Python 3.7+
- onnxruntime
- numpy
- Pillow (PIL)

## Quick Start

```python
import m3da

# Classify an image
result = m3da.execute(
    modelPath="path/to/your/model.onnx",
    pathToImage="path/to/your/image.jpg",
    classNames=["class1", "class2", "class3"],
    imgDimensions=(224, 224)
)

print(f"Predicted class: {result['class']}")
print(f"Confidence: {result['confidence']:.2f}")
print(f"Class index: {result['class_index']}")
```

## Parameters

The `execute()` function accepts the following parameters:

- `modelPath` (str): Path to the ONNX model file (must have .onnx extension)
- `pathToImage` (str): Path to the image file to classify
- `classNames` (list): List of class names corresponding to the model's output indices
- `imgDimensions` (tuple): Tuple of (width, height) for image resizing

## Return Value

The function returns a dictionary with the following keys:

- `class` (str): The predicted class name
- `confidence` (float): The confidence score for the prediction
- `class_index` (int): The index of the predicted class

## Example

Classifying an image of a pet using a pre-trained model:

```python
import m3da

classes = ["cat", "dog", "hamster", "rabbit", "goldfish"]

result = m3da.execute(
    modelPath="pet_classifier.onnx",
    pathToImage="my_pet.jpg",
    classNames=classes,
    imgDimensions=(32, 32)
)

print(f"This image appears to be a {result['class']} with {result['confidence']:.1%} confidence.")
```

## License

MIT
