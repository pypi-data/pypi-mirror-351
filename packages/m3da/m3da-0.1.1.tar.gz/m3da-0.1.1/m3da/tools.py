import onnxruntime as ort
import numpy as np
from PIL import Image
import os


class M3daTools:
    def __preprocessImage(self, image_path, input_size=(32, 32)):
        """
        Preprocess the image for model input:
        1. Open the image
        2. Resize to expected dimensions
        3. Convert to RGB if needed
        4. Convert to numpy array and normalize
        5. Transpose from HWC to CHW format (Height, Width, Channels -> Channels, Height, Width)
        6. Add batch dimension
        """
        # Open and resize image
        img = Image.open(image_path).convert("RGB")
        img = img.resize(input_size)

        # Convert to numpy and normalize to 0-1
        img_array = np.array(img).astype(np.float32) / 255.0

        # Transpose from HWC to CHW format
        img_array = img_array.transpose(2, 0, 1)

        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def __classifyImage(self, model_path, class_names, inputData):
        """
        Classify an image using an ONNX model
        """
        # Load ONNX model
        session = ort.InferenceSession(model_path)

        # Get input and output names
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name

        # Run inference
        results = session.run([output_name], {input_name: inputData})

        # Process results
        output = results[0]

        # Get the predicted class
        predicted_class_idx = np.argmax(output)
        predicted_class = class_names[predicted_class_idx]
        confidence = float(output[0][predicted_class_idx])

        return {
            "class": predicted_class,
            "confidence": confidence,
            "class_index": int(predicted_class_idx),
        }

    def __preCheck(
        self, modelPath: str, pathToImage: str, classNames: list, imgDimensions: tuple
    ):
        # pre
        assert isinstance(
            modelPath, str
        ), f"`modelPath` has to be a str; Got {type(modelPath)}"

        assert isinstance(
            pathToImage, str
        ), f"`Image` path has to be a str; Got {type(pathToImage)}"

        assert isinstance(
            classNames, list
        ), f"`classNames` has to be a list; Got {type(classNames)}"

        assert isinstance(
            imgDimensions, tuple
        ), f"`imgDimensions` has to be a tuple; Got {type(imgDimensions)}"

        # Verify that the model file is an ONNX file
        assert modelPath.lower().endswith(
            ".onnx"
        ), f"Model file must be an ONNX file with .onnx extension; Got {modelPath}"

        # ver
        assert os.path.isfile(modelPath), f"Model file not found: {modelPath}"
        assert os.path.isfile(pathToImage), f"Image file not found: {pathToImage}"

        # ver-2
        assert len(classNames) > 0 and all(
            [isinstance(name, str) and len(name.strip()) > 0 for name in classNames]
        ), f"Some provided class names appear invalid"

        assert (
            len(imgDimensions) > 0
        ), f"`imgDimensions` is empty; Requires two Integer values for image dimensions"

        assert (
            len(imgDimensions) == 2
        ), f"`imgDimensions` has more than two values; Requires two Integer values for image dimensions"

        assert (
            all([isinstance(dim, int) for dim in imgDimensions]) is True
        ), f"`imgDimensions` values have to be integers got: {imgDimensions}"

    def execute(
        self, modelPath: str, pathToImage: str, classNames: list, imgDimensions: tuple
    ):
        """
        Execute image classification with the provided ONNX model and image

        Args:
            modelPath (str): Path to the ONNX model file (.onnx extension)
            pathToImage (str): Path to the image file to classify
            classNames (list): List of class names corresponding to model outputs
            imgDimensions (tuple): Tuple of (width, height) for image resizing

        Returns:
            dict: Classification results with class name, confidence, and class index
        """
        # run check
        self.__preCheck(
            modelPath=modelPath,
            pathToImage=pathToImage,
            classNames=classNames,
            imgDimensions=imgDimensions,
        )

        # Preprocess image
        inputData = self.__preprocessImage(
            image_path=pathToImage,
            input_size=imgDimensions,
        )

        return self.__classifyImage(
            model_path=modelPath,
            class_names=classNames,
            inputData=inputData,
        )


# Create a module-level function for easier access
def classify_image(
    modelPath: str, pathToImage: str, classNames: list, imgDimensions: tuple
):
    """
    Direct function to classify an image with an ONNX model

    Args:
        modelPath (str): Path to the ONNX model file (.onnx extension)
        pathToImage (str): Path to the image file to classify
        classNames (list): List of class names corresponding to model outputs
        imgDimensions (tuple): Tuple of (width, height) for image resizing

    Returns:
        dict: Classification results with class name, confidence, and class index
    """
    tools = M3daTools()

    return tools.execute(modelPath, pathToImage, classNames, imgDimensions)
