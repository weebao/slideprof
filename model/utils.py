import fitz
from PIL import Image
import io

def extract_image_from_pdf(pdf_path, page_number, rect):
    """
    Extract an image from a specific coordinate on a given page in a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.
        page_number (int): Page number to extract image from (0-indexed).
        rect (tuple): A tuple with the coordinates of the rectangle (x0, y0, x1, y1).

    Returns:
        PIL.Image.Image: The extracted image from the specified rectangle.
    """
    document = fitz.open(pdf_path)
    
    page = document.load_page(page_number)
    rectangle = fitz.Rect(rect)
    pix = page.get_pixmap(clip=rectangle)
    
    document.close()
    image_data = pix.tobytes("png")
    image = Image.open(io.BytesIO(image_data))
    
    return image
