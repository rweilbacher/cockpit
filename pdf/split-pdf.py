import os
from PyPDF2 import PdfReader, PdfWriter


def split_pdf(pdf_path, config_path, output_dir):
    # Read the PDF file
    pdf = PdfReader(pdf_path)

    # Read the configuration file
    with open(config_path, 'r') as config_file:
        config_lines = config_file.readlines()

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Process each line in the configuration file
    file_number = 1
    for line in config_lines:
        # Split the line into page range and title
        title, page_range = line.strip().split('/', 1)
        start, end = map(int, page_range.split('-'))

        # Create a new PDF writer
        output_pdf = PdfWriter()

        # Add pages to the new PDF
        for page_num in range(start - 1, end):  # PyPDF2 uses 0-based indexing
            output_pdf.add_page(pdf.pages[page_num])

        # Save the new PDF
        output_filename = f"{file_number} - {title.replace(' ', '_')}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, 'wb') as output_file:
            output_pdf.write(output_file)

        print(f"Created: {output_path}")
        file_number += 1


if __name__ == "__main__":
    pdf_path = "./The Process of Creating Life_annotated_2024-09-09.pdf"
    config_path = "./split-config.txt"
    output_dir = "./output"

    split_pdf(pdf_path, config_path, output_dir)
    print("PDF splitting completed.")