# import fitz
# from PIL import Image
# import io

# def extract_image_from_pdf(pdf_path, page_number, rect):
#     """
#     Extract an image from a specific coordinate on a given page in a PDF file.

#     Args:
#         pdf_path (str): Path to the PDF file.
#         page_number (int): Page number to extract image from (0-indexed).
#         rect (tuple): A tuple with the coordinates of the rectangle (x0, y0, x1, y1).

#     Returns:
#         PIL.Image.Image: The extracted image from the specified rectangle.
#     """
#     document = fitz.open(pdf_path)
    
#     page = document.load_page(page_number)
#     rectangle = fitz.Rect(rect)
#     pix = page.get_pixmap(clip=rectangle)
    
#     document.close()
#     image_data = pix.tobytes("png")
#     image = Image.open(io.BytesIO(image_data))
    
#     return image



import fitz
from PIL import Image
import io

# def extract_image_from_pdf(pdf_path, page_number, pixel):
#     """
#     Extract an image from a specific pixel coordinate on a given page in a PDF file.

#     Args:
#         pdf_path (str): Path to the PDF file.
#         page_number (int): Page number to extract image from (0-indexed).
#         pixel (tuple): A tuple with the coordinates of the rectangle in pixels (x0, y0, x1, y1).

#     Returns:
#         PIL.Image.Image: The extracted image from the specified rectangle.
#     """
#     document = fitz.open(pdf_path)
    
#     page = document.load_page(page_number)
#     rect = fitz.Rect(pixel)
#     pix = page.get_pixmap(clip=rect)
    
#     document.close()
#     image_data = pix.tobytes("png")
#     image = Image.open(io.BytesIO(image_data))
    
#     return image


def extract_image_from_pdf(pdf_path, page_number, ratios):
    document = fitz.open(pdf_path)
    
    page = document.load_page(page_number)
    page_rect = page.rect
    x0 = page_rect.width * ratios[0]
    y0 = page_rect.height * ratios[1]
    x1 = page_rect.width * ratios[2]
    y1 = page_rect.height * ratios[3]
    rect = fitz.Rect(x0, y0, x1, y1)
    pix = page.get_pixmap(clip=rect)
    document.close()
    image_data = pix.tobytes("png")
    image = Image.open(io.BytesIO(image_data))
    
    return image

if __name__ == "__main__":
    pdf_path = "./test_input/lecture7.pdf"
    page_number = 0
    document = fitz.open(pdf_path)
    
    # Load the specified page
    page = document.load_page(page_number)
    
    # Get the dimensions of the page
    # Convert the dimensions from points to pixels
    zoom = 1  # 2x zoom for better resolution
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    width, height = pix.width, pix.height
    # Calculate the DPI (dots per inch) of the PDF
    page = document.load_page(page_number)
    page_rect = page.rect
    page_width_inch = page_rect.width / 72  # 1 point = 1/72 inch
    page_height_inch = page_rect.height / 72

    dpi_width = width / page_width_inch
    dpi_height = height / page_height_inch

    # Print the DPI
    print(f"DPI: {dpi_width} x {dpi_height}")
    # Print the dimensions
    print(f"Page dimensions: {width} x {height}")
    
    # Close the document
    document.close()
    page_number = 0
    pixel = (0.25, 0.25, 0.75, 0.75)
    image = extract_image_from_pdf(pdf_path, page_number, pixel)
    image.show()    