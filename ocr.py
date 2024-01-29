import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from logger import logger_msg


pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH')

def extract_text(file, input_path, lang='eng'):
    logger_msg("Inside extract_text function")
    logger_msg(f"Tesseract path: {os.getenv('TESSERACT_PATH')}")

    if input_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        image = Image.open(file)
        text = pytesseract.image_to_string(image, lang=lang)
    elif input_path.lower().endswith('.pdf'):
        pdf_document = fitz.open("pdf", file.read())
        pdf_text = []
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            image_data = pix.tobytes("png")  # Convert the image data to PNG format
            image = Image.open(io.BytesIO(image_data))
            page_text = pytesseract.image_to_string(image, lang=lang)
            pdf_text.append(f"Page {page_num + 1}:\n{page_text}")
        text = "\n".join(pdf_text)
        pdf_document.close()
    else:
        raise ValueError("Unsupported file format. Use an image (png, jpg, etc.) or a PDF.")

    return text
