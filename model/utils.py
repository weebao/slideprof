import fitz
from PIL import Image
import io
from moviepy.editor import VideoFileClip
import os
import cv2
import numpy as np


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

def mp4_to_voice(mp4_path):
    """
    Convert an MP4 file to a WAV file using FFmpeg.

    Args:
        mp4_path (str): Path to the MP4 file.

    Returns:
        str: Path to the output file.
    """
    video = VideoFileClip(mp4_path)

    audio = video.audio
    audio.write_audiofile("./test_input/output_audio.mp3")
    
    return "./test_input/output_audio.mp3"

def extract_pages_from_pdf(pdf_path, output_folder, image_format='png'):
    """
    Extract each page from a PDF file and save it as a separate PDF file.
    """
    pdf_document = fitz.open(pdf_path)
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)  
        pix = page.get_pixmap() 
        output_image_path = os.path.join(output_folder, f'page_{page_num + 1}.{image_format}')
        pix.save(output_image_path)
        
        print(f"Page {page_num + 1} saved as {output_image_path}")

    pdf_document.close()

# if __name__ == "__main__":
    
    
    