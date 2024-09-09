import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set the path to the Poppler binaries if not in system PATH
poppler_path = None  # Set this to the Poppler path if it's not in your system PATH


def ocr_image(image):
    try:
        text = pytesseract.image_to_string(image)
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