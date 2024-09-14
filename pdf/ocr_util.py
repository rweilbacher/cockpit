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
import sys
import shutil


# Set the path to the Poppler binaries if not in system PATH
poppler_path = None  # Set this to the Poppler path if it's not in your system PATH

# For debug purposes
similarities = []

DEBUG = True


# Set the path to the log file
LOG_FILE_PATH = '../pdf/output/ocr_util.log'


# Set up logging
def setup_logging(log_file_path):
    class TeeStream(object):
        def __init__(self, stream, file):
            self.stream = stream
            self.file = file

        def write(self, data):
            self.stream.write(data)
            self.file.write(data)
            self.flush()

        def flush(self):
            self.stream.flush()
            self.file.flush()

    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = open(log_file_path, 'w')
    sys.stdout = TeeStream(sys.stdout, log_file)
    sys.stderr = TeeStream(sys.stderr, log_file)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.StreamHandler(sys.stdout),
                            logging.FileHandler(log_file_path)
                        ])
    return logging.getLogger(__name__)


def preprocess_image(image):
    # Convert PIL Image to OpenCV format
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Cut 190 off the top and 150 off the bottom
    height, width = img.shape[:2]
    img = img[190:height - 150, :]

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply adaptive thresholding to get binary image
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Find contours on the binary image
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  # Return cropped image if no contours found

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


def remove_hlt_color(image, color_ranges):
    # Convert image to HSV
    hsv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2HSV)
    img_arr = np.array(image)

    # Create a mask for all specified color ranges
    mask = np.zeros(hsv_image.shape[:2], dtype=np.uint8)

    for color, (lower, upper) in color_ranges.items():
        color_mask = cv2.inRange(hsv_image, lower, upper)
        mask = cv2.bitwise_or(mask, color_mask)

    # Invert the mask
    inv_mask = cv2.bitwise_not(mask)

    # Create a white image of the same size as the input image
    white = np.ones(img_arr.shape, dtype=np.uint8) * 255

    # Use the inverted mask to combine the original image and the white image
    result = cv2.bitwise_and(img_arr, img_arr, mask=inv_mask)
    result += cv2.bitwise_and(white, white, mask=mask)

    return Image.fromarray(result)


def preprocess_hlt(image):
    image = remove_hlt_color(image, extract_highlights.COLOR_RANGES_HSV)
    # image = preprocess_image(image)
    return image


def ocr_image(image, psm, output_path, logger, preprocess=False, hlt=False, print_osd=False, page_number=None):
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
            visualize_layout(image, data, page_number, output_path, logger)
            if not hlt:
                analyze_page_accuracy(data, page_number, output_path, logger)

        return text
    except pytesseract.TesseractError as e:
        logger.exception(f"Tesseract error: {e}")
        return "OCR failed"


def visualize_layout(image, data, page_number, output_dir, logger):
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


def calculate_word_accuracy_percentages(data):
    # Define the new confidence buckets
    buckets = {
        '0-40%': 0,
        '40-60%': 0,
        '60-80%': 0,
        '80-90%': 0,
        '90-100%': 0
    }

    total_words = 0

    # Iterate through the words in the data
    for i in range(len(data['text'])):
        if data['text'][i].strip():  # Only consider non-empty words
            confidence = float(data['conf'][i])
            total_words += 1

            if confidence < 40:
                buckets['0-40%'] += 1
            elif confidence < 60:
                buckets['40-60%'] += 1
            elif confidence < 80:
                buckets['60-80%'] += 1
            elif confidence < 90:
                buckets['80-90%'] += 1
            else:
                buckets['90-100%'] += 1

    # Calculate percentages
    percentages = {}
    for bucket, count in buckets.items():
        percentage = (count / total_words) * 100 if total_words > 0 else 0
        percentages[bucket] = round(percentage, 2)

    return percentages, total_words


def analyze_page_accuracy(data, page_number, output_dir, logger):
    percentages, total_words = calculate_word_accuracy_percentages(data)

    # Create a single line log string
    log_parts = [f"Page {page_number}"]
    log_parts.extend([f"{bucket}: {percentage}%" for bucket, percentage in percentages.items()])
    log_parts.append(f"Total words: {total_words}")
    log_string = " | ".join(log_parts)

    # Log the results in a single line
    logger.info(log_string)

    # Optionally, save to a file
    output_file = os.path.join(output_dir, f'word_accuracy_page_{page_number}.txt')
    with open(output_file, 'w') as f:
        f.write(log_string + '\n')


def ocr_pdf(clean_pdf_path, highlighted_pdf_path, output_path, logger, psm=1, cleanup_text=True, match_highlights=True):
    # Find the end of the current word
    def find_word_end(text, index):
        while index < len(text) and not text[index].isspace():
            index += 1
        return index

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
            text = ocr_image(image, psm, output_path, logger, preprocess=True, page_number=page_num)
            # TODO move this after the highlight matching (or test if that makes anything better)
            if cleanup_text:
                text = process_text(text)

            if match_highlights:
                # Extract highlights from the corresponding highlighted image
                highlights = extract_highlights.extract_highlights(highlighted_images[i], i, output_path, logger)
                for highlight in reversed(highlights):
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

                        # Check if the highlight ends in the middle of a word
                        if end_index < len(text) and not text[end_index].isspace():
                            # If so, extend the end_index to the end of the word
                            end_index = find_word_end(text, end_index)

                        # Ensure we don't go beyond the text length
                        end_index = min(end_index, len(text))

                        # First, look for the start of a span tag
                        span_start = text.rfind("<span", start_index, end_index)
                        if span_start != -1:
                            # If found, move end_index to just before the span starts
                            end_index = span_start
                            # Adjust start_index if necessary
                            start_index = min(start_index, span_start)

                        # Now look for the end of a span tag
                        span_end = text.find("</span>", start_index, end_index)
                        if span_end != -1:
                            shift = (span_end + 7) - start_index
                            new_start_index = span_end + 7
                            new_end_index = min(end_index + shift, len(text))
                            start_index = new_start_index
                            end_index = new_end_index

                        span = f"<span match=\"{similarity}%\" class={css_class}>"
                        highlighted_section = span + text[start_index:end_index] + "</span>"
                        text = text[:start_index] + highlighted_section + text[end_index:]
                    else:
                        logger.error(f"Error: No match found for highlight on page {i+1}")
                        similarities.append(0)
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
    text = re.sub(r'(\w+)-\s(\w+)', r'\1\2', text)

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


def process_pdf_files(input_folder: str, output_base_folder: str):
    # Get all PDF files in the input folder
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]

    # Group files by their base name
    file_groups = {}
    for pdf_file in pdf_files:
        if pdf_file.endswith('_clean.pdf'):
            base_name = pdf_file[:-10]  # Remove '_clean.pdf'
            if base_name not in file_groups:
                file_groups[base_name] = {'clean': None, 'hlted': None}
            file_groups[base_name]['clean'] = pdf_file
        elif pdf_file.endswith('_hlted.pdf'):
            base_name = pdf_file[:-10]  # Remove '_hlted.pdf'
            if base_name not in file_groups:
                file_groups[base_name] = {'clean': None, 'hlted': None}
            file_groups[base_name]['hlted'] = pdf_file

    # Process each group of files
    for base_name, files in file_groups.items():
        if files['clean'] and files['hlted']:
            clean_pdf = os.path.join(input_folder, files['clean'])
            highlighted_pdf = os.path.join(input_folder, files['hlted'])

            # Create output folder
            output_folder = os.path.join(output_base_folder, base_name)
            os.makedirs(output_folder, exist_ok=True)

            # Setup logging
            logger = setup_logging(os.path.join(output_folder, "ocr_util.log"))

            # Run OCR
            pdf_text = ocr_pdf(clean_pdf, highlighted_pdf, output_folder, logger)

            # Write the full text to a markdown file
            output_file = os.path.join(output_folder, "ocr_result.md")
            with open(output_file, 'w', encoding='utf-8') as md_file:
                md_file.write(pdf_text)

            # Copy original PDFs to output folder
            shutil.copy2(clean_pdf, output_folder)
            shutil.copy2(highlighted_pdf, output_folder)

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
            logger.info(f"Similarity - min={min_sim} max={max_sim} avg={avg_sim}")

            logger.info(f"Processed {base_name}")
        else:
            logger.warning(f"Incomplete set of files for {base_name}")


if __name__ == "__main__":
    input_folder = "../pdf/output"
    output_base_folder = "../pdf/output"

    process_pdf_files(input_folder, output_base_folder)
