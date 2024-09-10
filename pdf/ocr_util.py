import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import logging
import re
import cv2
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set the path to the Poppler binaries if not in system PATH
poppler_path = None  # Set this to the Poppler path if it's not in your system PATH


def preprocess_image(image):
    # Convert PIL Image to OpenCV format
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

    # Deskew
    coords = np.column_stack(np.where(denoised > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(denoised, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Convert back to PIL Image
    return Image.fromarray(rotated)


def ocr_image(image):
    try:
        # Preprocess the image
        processed_image = preprocess_image(image)

        # Configure Tesseract
        custom_config = r'--oem 3 --psm 1 -c preserve_interword_spaces=1'

        # Perform OCR
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        return text
    except pytesseract.TesseractError as e:
        logger.error(f"Tesseract error: {e}")
        return "OCR failed"


def ocr_pdf(file_path):
    try:
        # Convert PDF to images
        if poppler_path:
            images = convert_from_path(file_path, poppler_path=poppler_path)
        else:
            images = convert_from_path(file_path)

        # Perform OCR on the images
        ocr_text = ""
        for i, image in enumerate(images):
            text = ocr_image(image)
            ocr_text += f"Page {i + 1}:\n{text}\n\n"

        return ocr_text

    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return None


def ocr_image_file(file_path):
    try:
        # Open image file
        with Image.open(file_path) as image:
            ocr_text = ocr_image(image)

        return ocr_text

    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return None


if __name__ == "__main__":
    # This block is for testing the module independently
    test_pdf = "path/to/test.pdf"
    test_image = "path/to/test.png"

    pdf_text = ocr_pdf(test_pdf)
    if pdf_text:
        print("PDF OCR Result:")
        print(pdf_text[:500])  # Print first 500 characters as a sample

    image_text = ocr_image_file(test_image)
    if image_text:
        print("\nImage OCR Result:")
        print(image_text[:500])  # Print first 500 characters as a sample
