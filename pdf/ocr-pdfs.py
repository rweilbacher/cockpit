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
        logging.error(f"Tesseract error: {e}")
        return "OCR failed"


def process_text(text):
    # Replace single newlines with spaces
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    # Remove any remaining single CR characters
    text = re.sub(r'(?<!\r)\r(?!\r)', ' ', text)

    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)

    # Ensure paragraphs are separated by double newlines
    text = re.sub(r'\n{2,}', '\n\n', text)

    # Reformat words that were split across lines
    text = re.sub(r'(\w+)-\s\n(\w+)', r'\1\2', text)

    return text.strip()


def process_file(file_path, output_dir):
    filename = os.path.basename(file_path)
    base_name = os.path.splitext(filename)[0]

    try:
        if filename.lower().endswith('.pdf'):
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

        elif filename.lower().endswith('.png'):
            # Open PNG file
            with Image.open(file_path) as image:
                ocr_text = ocr_image(image)

        else:
            logging.warning(f"Unsupported file type: {filename}")
            return

        # Process the OCR text
        processed_text = process_text(ocr_text)

        # Save processed OCR text
        txt_filename = f"{base_name}_OCR.txt"
        txt_path = os.path.join(output_dir, txt_filename)
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(processed_text)

        logging.info(f"Created processed OCR text for {filename}: {txt_path}")

    except Exception as e:
        logging.error(f"Error processing {filename}: {e}")


def process_directory(input_dir, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Iterate through all files in the directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.pdf', '.png')):
            file_path = os.path.join(input_dir, filename)
            process_file(file_path, output_dir)


if __name__ == "__main__":
    input_dir = "./output"  # Directory containing the input files
    output_dir = "./output"  # Directory for output OCR text files

    # Check if the input directory exists
    if not os.path.isdir(input_dir):
        logging.error(f"Input directory not found: {input_dir}")
    else:
        process_directory(input_dir, output_dir)
        logging.info("OCR processing completed.")