import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import logging
import re
import extract_highlights
from fuzzywuzzy import fuzz

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
        logger.exception(f"Tesseract error: {e}")
        return "OCR failed"


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
            text = ocr_image(image, psm)
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
    clean_pdf = "../pdf/mixed_columns_clean.pdf"
    highlighted_pdf = "../pdf/mixed_columns_highlighted.pdf"

    # For multi-column PDF
    pdf_text = ocr_pdf(clean_pdf, highlighted_pdf)
    # Write the full text to a markdown file
    output_file = os.path.join("../pdf/output", "ocr_result.md")
    with open(output_file, 'w', encoding='utf-8') as md_file:
        md_file.write(pdf_text)

    print(f"\nFull OCR result written to: {output_file}")

