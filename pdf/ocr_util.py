import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import logging
import re
import extract_highlights
from fuzzywuzzy import fuzz
import cv2
import numpy as np
import subprocess
import tempfile

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set the path to the Poppler binaries if not in system PATH
poppler_path = None  # Set this to the Poppler path if it's not in your system PATH

# For debug purposes
similarities = []

DEBUG = True


def preprocess_image(image):
    # Convert PIL Image to OpenCV format
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply adaptive thresholding to get binary image
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Find contours on the binary image
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return image  # Return original image if no contours found

    # Find the bounding box of the content
    x_min, y_min, x_max, y_max = float('inf'), float('inf'), 0, 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + w)
        y_max = max(y_max, y + h)

    # Calculate the center of the content
    content_center_x = (x_min + x_max) // 2
    content_center_y = (y_min + y_max) // 2

    # Calculate the center of the image
    h, w = binary.shape[:2]
    image_center_x, image_center_y = w // 2, h // 2

    # Calculate the translation
    tx = image_center_x - content_center_x
    ty = image_center_y - content_center_y

    # Create the translation matrix
    M = np.float32([[1, 0, tx], [0, 1, ty]])

    # Apply the translation to the binary image
    centered = cv2.warpAffine(binary, M, (w, h), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT,
                              borderValue=255)

    # Convert back to PIL Image
    return Image.fromarray(centered)


def preprocess_hlt(image):
    return image


def ocr_image(image, psm, preprocess=False, hlt=False, print_osd=False, page_number=None, output_dir='../pdf/output'):
    try:
        if preprocess and not hlt:
            image = preprocess_image(image)
        elif preprocess and hlt:
            image = preprocess_hlt(image)

        # Configure Tesseract
        custom_config = f'--oem 3 --psm {psm} -c preserve_interword_spaces=1'

        # Perform OCR
        text = pytesseract.image_to_string(image, config=custom_config)

        # Perform OSD
        if print_osd and page_number is not None:
            osd = pytesseract.image_to_osd(image)
            print(f"OSD pg {page_number}: {osd}")

        # Visualize layout analysis
        if page_number is not None:
            data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
            visualize_layout(image, data, page_number, output_dir)

        return text
    except pytesseract.TesseractError as e:
        logger.exception(f"Tesseract error: {e}")
        return "OCR failed"


def visualize_layout(image, data, page_number, output_dir):
    # Create a drawing object
    draw = ImageDraw.Draw(image)

    # Draw rectangles for each detected text element
    for i in range(len(data['level'])):
        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
        draw.rectangle([x, y, x + w, y + h], outline="red")

    # Save the annotated image
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, f'tesseract_info_{page_number}.png')
    image.save(output_path)
    logger.info(f"Saved annotated image to {output_path}")


def ocr_pdf(clean_pdf_path, highlighted_pdf_path, psm=1, cleanup_text=True, match_highlights=True):
    try:
        # Convert clean PDF to images
        if poppler_path:
            clean_images = convert_from_path(clean_pdf_path, poppler_path=poppler_path)
            highlighted_images = convert_from_path(highlighted_pdf_path, poppler_path=poppler_path)
        else:
            clean_images = convert_from_path(clean_pdf_path)
            highlighted_images = convert_from_path(highlighted_pdf_path)

        # Perform OCR on the clean images
        ocr_text = ""
        for i, image in enumerate(clean_images):
            page_num = i + 1
            ocr_text += f"\nPage: {page_num}\n"
            text = ocr_image(image, psm, preprocess=True, page_number=page_num)
            # TODO move this after the highlight matching
            if cleanup_text:
                text = process_text(text)

            if match_highlights:
                # Extract highlights from the corresponding highlighted image
                highlights = extract_highlights.extract_highlights(highlighted_images[i], i, "../pdf/output")
                for highlight in highlights:
                    match_result = find_highlight_in_text(highlight["text"], text)
                    if match_result:
                        start_index, end_index, similarity = match_result
                        if DEBUG:
                            similarities.append(similarity)
                        logger.info(f"Highlight found: '{text[start_index:end_index][:20]}' (Similarity: {similarity}%)")
                        if highlight["color"] == "yellow":
                            css_class = "\"hlt-ylw\""
                        elif highlight["color"] == "green":
                            css_class = "\"hlt-grn\""
                        elif highlight["color"] == "red":
                            css_class = "\"hlt-red\""
                        elif highlight["color"] == "purple":
                            css_class = "\"hlt-prp\""
                        else:
                            css_class = "\"hlt-ylw\""
                            logger.error(f"Error: Unrecognized color {highlight['color']}")
                        span = f"<span match=\"{similarity}%\" class={css_class}>"
                        highlighted_section = span + text[start_index:end_index] + "</span>"
                        text = text[:start_index] + highlighted_section + text[end_index:]
                    else:
                        logger.error(f"Error: No match found for highlight on page {i+1}")
            ocr_text += text

        return ocr_text

    except Exception as e:
        logger.exception(f"Error processing PDFs: {e}")
        return None


def ocr_image_file(file_path, psm=6):
    try:
        # Open image file
        with Image.open(file_path) as image:
            ocr_text = ocr_image(image, psm)

        return ocr_text

    except Exception as e:
        logger.exception(f"Error processing {file_path}: {e}")
        return None


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


def find_highlight_in_text(highlight_text, full_text, threshold=0):
    def find_word_end(text, start_index):
        match = re.search(r'\s', text[start_index:])
        return start_index + match.start() if match else len(text)

    def find_next_word_start(text, start_index):
        word_end = find_word_end(text, start_index)
        match = re.search(r'\S', text[word_end:])
        return word_end + match.start() if match else len(text)

    highlight_length = len(highlight_text)
    full_length = len(full_text)

    best_match = None
    best_score = 0
    window_start = 0

    while window_start + highlight_length <= full_length:
        window_text = full_text[window_start:window_start + highlight_length]
        score = fuzz.ratio(highlight_text, window_text)

        if score > best_score and score >= threshold:
            best_score = score
            best_match = (window_start, window_start + highlight_length, score)

        # Move the window to the start of the next word
        window_start = find_next_word_start(full_text, window_start)

    return best_match  # This will be None if no match is found


if __name__ == "__main__":
    # This block is for testing the module independently
    # clean_pdf = "../pdf/mixed_columns_clean.pdf"
    # highlighted_pdf = "../pdf/mixed_columns_highlighted.pdf"

    # test_pdf = "../pdf/The gentle breeze whispered through the trees.pdf"
    # ocr_pdf(test_pdf, test_pdf, match_highlights=False)

    clean_pdf = "../pdf/clean.pdf"
    highlighted_pdf = "../pdf/annotated.pdf"

    # For multi-column PDF
    pdf_text = ocr_pdf(clean_pdf, highlighted_pdf)
    # Write the full text to a markdown file
    output_file = os.path.join("../pdf/output", "ocr_result.md")
    with open(output_file, 'w', encoding='utf-8') as md_file:
        md_file.write(pdf_text)

    if DEBUG:
        min_sim = 101
        max_sim = -1
        sum = 0
        for similarity in similarities:
            sum += similarity
            if similarity < min_sim:
                min_sim = similarity
            if similarity > max_sim:
                max_sim = similarity
        avg_sim = sum / len(similarities)
        print(f"Similarity info - min={min_sim} max={max_sim} avg={avg_sim}")



    print(f"\nFull OCR result written to: {output_file}")

