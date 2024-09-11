import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set the path to the Poppler binaries if not in system PATH
poppler_path = None  # Set this to the Poppler path if it's not in your system PATH


def ocr_image(image, psm):
    try:
        # Configure Tesseract
        custom_config = f'--oem 3 --psm {psm} -c preserve_interword_spaces=1'

        # Perform OCR
        text = pytesseract.image_to_string(image, config=custom_config)
        return text
    except pytesseract.TesseractError as e:
        logger.error(f"Tesseract error: {e}")
        return "OCR failed"


def ocr_pdf(file_path, psm=1):
    try:
        # Convert PDF to images
        if poppler_path:
            images = convert_from_path(file_path, poppler_path=poppler_path)
        else:
            images = convert_from_path(file_path)

        # Perform OCR on the images
        ocr_text = ""
        for i, image in enumerate(images):
            text = ocr_image(image, psm)
            ocr_text += f"Page {i + 1}:\n{text}\n\n"

        return ocr_text

    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return None


def ocr_image_file(file_path, psm=6):
    try:
        # Open image file
        with Image.open(file_path) as image:
            ocr_text = ocr_image(image, psm)

        return ocr_text

    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return None


if __name__ == "__main__":
    # This block is for testing the module independently
    test_pdf = "path/to/test.pdf"
    test_image = "path/to/test.png"

    # For multi-column PDF
    pdf_text = ocr_pdf(test_pdf, psm=3)
    if pdf_text:
        print("PDF OCR Result:")
        print(pdf_text[:500])  # Print first 500 characters as a sample

    # For extracting highlights
    image_text = ocr_image_file(test_image, psm=11)
    if image_text:
        print("\nImage OCR Result:")
        print(image_text[:500])  # Print first 500 characters as a sample
