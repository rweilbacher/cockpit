import fitz  # PyMuPDF
import numpy as np
import cv2
from PIL import Image
import logging
from typing import List, Dict, Tuple
import os
from ocr_util import ocr_image_file

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Minimum size for highlighted areas (in pixels)
MIN_HIGHLIGHT_AREA = 100  # Adjust this value as needed

# Define color ranges in HSV
COLOR_RANGES = {
    'yellow': (np.array([28, 80, 200]), np.array([32, 255, 255])),
    'green': (np.array([64, 95, 200]), np.array([68, 255, 255])),
    'red': (np.array([0, 95, 200]), np.array([6, 255, 255])),
    'purple': (np.array([150, 80, 200]), np.array([159, 255, 255]))
}


def pdf_to_images(pdf_path: str) -> List[np.ndarray]:
    try:
        doc = fitz.open(pdf_path)
        images = []
        for page_num in range(len(doc)):
            try:
                pix = doc[page_num].get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(np.array(img))
                logger.info(f"Processed page {page_num + 1}")
            except Exception as e:
                logger.error(f"Error processing page {page_num + 1}: {str(e)}")
        return images
    except Exception as e:
        logger.error(f"Error opening PDF file: {str(e)}")
        raise


def extract_highlights(annotated_images: List[np.ndarray], unannotated_images: List[np.ndarray], output_folder: str) -> \
List[Dict]:
    highlighted_areas = []
    for page_num, (annotated_img, unannotated_img) in enumerate(zip(annotated_images, unannotated_images)):
        image_filename = f"unannotated_page{page_num + 1}.png"
        image_path = os.path.join(output_folder, image_filename)
        cv2.imwrite(image_path, cv2.cvtColor(unannotated_img, cv2.COLOR_RGB2BGR))
        image_filename = f"annotated{page_num + 1}.png"
        image_path = os.path.join(output_folder, image_filename)
        cv2.imwrite(image_path, cv2.cvtColor(annotated_img, cv2.COLOR_RGB2BGR))
        try:
            hsv = cv2.cvtColor(annotated_img, cv2.COLOR_RGB2HSV)
            for color, (lower, upper) in COLOR_RANGES.items():
                mask = cv2.inRange(hsv, lower, upper)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for i, contour in enumerate(contours):
                    area = cv2.contourArea(contour)
                    if area < MIN_HIGHLIGHT_AREA:
                        continue  # Skip this contour if it's too small

                    x, y, w, h = cv2.boundingRect(contour)

                    # Extract the highlighted area from the annotated image
                    highlight_image = annotated_img[y:y + h, x:x + w]
                    # Save the highlighted area as a PNG image
                    image_filename = f"annotated_highlight_page{page_num + 1}_{color}_{i + 1}_area{int(area)}.png"
                    image_path = os.path.join(output_folder, image_filename)
                    cv2.imwrite(image_path, cv2.cvtColor(highlight_image, cv2.COLOR_RGB2BGR))

                    # Extract the highlighted area from the unannotated image
                    highlight_image = unannotated_img[y:y + h, x:x + w]
                    # Save the highlighted area as a PNG image
                    image_filename = f"highlight_page{page_num + 1}_{color}_{i + 1}_area{int(area)}.png"
                    image_path = os.path.join(output_folder, image_filename)
                    cv2.imwrite(image_path, cv2.cvtColor(highlight_image, cv2.COLOR_RGB2BGR))


                    # Perform OCR on the highlight image
                    highlight_text = ocr_image_file(image_path)

                    highlighted_area = {
                        'color': color,
                        'page': page_num + 1,
                        'bbox': (x, y, x + w, y + h),
                        'image_path': image_path,
                        'area': area,
                        'text': highlight_text
                    }
                    highlighted_areas.append(highlighted_area)
                    logger.info(f"Processed highlight: {image_filename}")

            logger.info(f"Extracted highlights from page {page_num + 1}")
        except Exception as e:
            logger.error(f"Error extracting highlights from page {page_num + 1}: {str(e)}")
    return highlighted_areas


def generate_markdown(highlighted_areas: List[Dict], output_folder: str, pdf_name: str):
    markdown_content = f"# Highlights from {pdf_name}\n\n"
    for area in highlighted_areas:
        markdown_content += f"## Page {area['page']} - {area['color'].capitalize()} Highlight\n\n"
        markdown_content += f"Text: {area['text']}\n\n"
        markdown_content += f"![Highlight](/{area['image_path']})\n\n"
        markdown_content += "---\n\n"

    markdown_path = os.path.join(output_folder, f"{pdf_name}_highlights.md")
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    logger.info(f"Generated markdown file: {markdown_path}")


def process_pdfs(annotated_pdf_path: str, unannotated_pdf_path: str, output_folder: str) -> List[Dict]:
    try:
        os.makedirs(output_folder, exist_ok=True)
        logger.info(
            f"Starting processing of PDFs:\nAnnotated: {annotated_pdf_path}\nUnannotated: {unannotated_pdf_path}")

        pdf_name = os.path.splitext(os.path.basename(annotated_pdf_path))[0]

        # Convert both PDFs to images
        annotated_images = pdf_to_images(annotated_pdf_path)
        unannotated_images = pdf_to_images(unannotated_pdf_path)

        # Extract and process highlights
        highlighted_areas = extract_highlights(annotated_images, unannotated_images, output_folder)

        # Generate markdown for highlights
        generate_markdown(highlighted_areas, output_folder, pdf_name)

        logger.info(f"Completed processing. Found {len(highlighted_areas)} highlighted areas.")
        return highlighted_areas
    except Exception as e:
        logger.error(f"An error occurred during processing: {str(e)}")
        return []


if __name__ == "__main__":
    # This block is for testing the module independently
    ANNOTATED_PDF_PATH = "C:\\Users\\Roland\\Google Drive\\Projects\\cockpit\\pdf\\annotated.pdf"
    UNANNOTATED_PDF_PATH = "C:\\Users\\Roland\\Google Drive\\Projects\\cockpit\\pdf\\unannotated.pdf"
    OUTPUT_FOLDER = "C:\\Users\\Roland\\Google Drive\\Projects\\cockpit\\pdf\\output"
    highlighted_areas = process_pdfs(ANNOTATED_PDF_PATH, UNANNOTATED_PDF_PATH, OUTPUT_FOLDER)

    # Example of using the results
    for area in highlighted_areas:
        logger.info(
            f"Found {area['color']} highlight on page {area['page']} at position {area['bbox']} with area {area['area']}. Text: {area['text'][:50]}...")