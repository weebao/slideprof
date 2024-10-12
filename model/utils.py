import fitz  

def extract_text_from_pdf(pdf_path, page_number, rect):
    """
    Extract text from a specific coordinate on a given page in a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.
        page_number (int): Page number to extract text from (0-indexed).
        rect (tuple): A tuple with the coordinates of the rectangle (x0, y0, x1, y1).

    Returns:
        str: The extracted text from the specified rectangle.
    """
    document = fitz.open(pdf_path)
    page = document.load_page(page_number)
    rectangle = fitz.Rect(rect)
    text = page.get_text("text", clip=rectangle)
    document.close()

    return text

