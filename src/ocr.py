import cv2
import pytesseract

def extract_text_from_cell(cell_image):
    """Extract text from a single cell image using Tesseract OCR."""
    config = '--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'
    text = pytesseract.image_to_string(cell_image, config=config)
    return text.strip()

def process_cells(cells):
    """Process a list of cell images and return the extracted text."""
    extracted_text = []
    for cell in cells:
        text = extract_text_from_cell(cell)
        extracted_text.append(text)
    return extracted_text