import fitz  # PyMuPDF
import numpy as np
import cv2
from PIL import Image
import logging
from typing import List, Dict, Tuple
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Hardcode the PDF path here
PDF_PATH = "./annotated.pdf"
OUTPUT_FOLDER = "./output"


def ensure_output_folder():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        logger.info(f"Created output folder: {OUTPUT_FOLDER}")


def pdf_to_images(pdf_path: str) -> List[np.ndarray]:
    try:
        doc = fitz.open(pdf_path)
        images = []
        for page_num, page in enumerate(doc):
            try:
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(np.array(img))
                logger.info(f"Processed page {page_num + 1}")
            except Exception as e:
                logger.error(f"Error processing page {page_num + 1}: {str(e)}")
        return images
    except Exception as e:
        logger.error(f"Error opening PDF file: {str(e)}")
        raise


def extract_highlights(images: List[np.ndarray], color_ranges: Dict[str, Tuple[np.ndarray, np.ndarray]]) -> List[Dict]:
    highlighted_areas = []
    for page_num, img in enumerate(images):
        try:
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            for color, (lower, upper) in color_ranges.items():
                mask = cv2.inRange(hsv, lower, upper)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for i, contour in enumerate(contours):
                    x, y, w, h = cv2.boundingRect(contour)
                    highlighted_area = {
                        'color': color,
                        'page': page_num + 1,
                        'bbox': (x, y, x + w, y + h),
                        'image': img[y:y + h, x:x + w]
                    }
                    highlighted_areas.append(highlighted_area)

                    # Save the highlighted area as a PNG image
                    image_filename = f"highlight_page{page_num + 1}_{color}_{i + 1}.png"
                    image_path = os.path.join(OUTPUT_FOLDER, image_filename)
                    cv2.imwrite(image_path, cv2.cvtColor(highlighted_area['image'], cv2.COLOR_RGB2BGR))
                    logger.info(f"Saved highlighted area: {image_filename}")

            logger.info(f"Extracted highlights from page {page_num + 1}")
        except Exception as e:
            logger.error(f"Error extracting highlights from page {page_num + 1}: {str(e)}")
    return highlighted_areas


def main() -> List[Dict]:
    try:
        ensure_output_folder()
        logger.info(f"Starting processing of PDF: {PDF_PATH}")
        images = pdf_to_images(PDF_PATH)

        # Define color ranges in HSV
        color_ranges = {
            'yellow': (np.array([20, 100, 100]), np.array([30, 255, 255])),
            'red': (np.array([0, 100, 100]), np.array([10, 255, 255])),
            'green': (np.array([40, 100, 100]), np.array([80, 255, 255]))
        }

        highlighted_areas = extract_highlights(images, color_ranges)
        logger.info(f"Completed processing. Found {len(highlighted_areas)} highlighted areas.")
        return highlighted_areas
    except Exception as e:
        logger.error(f"An error occurred during processing: {str(e)}")
        return []


if __name__ == "__main__":
    highlighted_areas = main()

    # Example of using the results
    for area in highlighted_areas:
        logger.info(f"Found {area['color']} highlight on page {area['page']} at position {area['bbox']}")