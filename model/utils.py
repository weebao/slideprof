import fitz
from PIL import Image
import io
from moviepy.editor import VideoFileClip
import os
import cv2
import numpy as np
import time
import multiprocessing
from tqdm import tqdm
import json


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

# def extract_keyframes_on_scene_change(video_path, output_folder, threshold=0.5):
#     cap = cv2.VideoCapture(video_path)
#     prev_hist = None
#     frame_count = 0
#     extracted_frames = []
    
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
        
#         hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
#         hist = cv2.normalize(hist, hist).flatten()
        
#         if prev_hist is None:
#             prev_hist = hist
#             continue
        
#         hist_diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
        
#         if hist_diff < threshold:
#             extracted_frames.append((frame_count / cap.get(cv2.CAP_PROP_FPS), frame))
        
#         prev_hist = hist
#         frame_count += 1
    
#     cap.release()
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)

#     for idx, (timestamp, frame) in enumerate(extracted_frames):
#         output_image_path = os.path.join(output_folder, f'frame_{idx + 1}.png')
#         cv2.imwrite(output_image_path, frame)
#         print(f"Frame at {timestamp:.2f}s saved as {output_image_path}")

#     return output_folder

def process_frame(args):
    frame, prev_hist, threshold = args
    new_hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    new_hist = cv2.normalize(new_hist, new_hist).flatten()
    hist_diff = cv2.compareHist(prev_hist, new_hist, cv2.HISTCMP_CORREL)
    is_scene_change = hist_diff < threshold
    return new_hist, is_scene_change

def extract_keyframes_parallel(video_path, output_folder, json_output_path, threshold=0.5, interval_seconds=0.4):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    frame_interval = int(fps * interval_seconds)
    
    prev_hist = None
    frame_count = 0
    extracted_frames = []
    
    start_time = time.time()
    frame_data_list = []
    frame_timestamps = []
    
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool, tqdm(total=total_frames, desc="Processing frames") as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval != 0:
                frame_count += 1
                pbar.update(1)
                continue

            if prev_hist is None:
                prev_hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                prev_hist = cv2.normalize(prev_hist, prev_hist).flatten()
                frame_count += 1
                pbar.update(1)
                continue

            frame_data_list.append((frame, prev_hist, threshold))

            results = pool.map(process_frame, frame_data_list)

            for idx, (new_hist, is_scene_change) in enumerate(results):
                if is_scene_change:
                    timestamp = frame_count / fps
                    extracted_frames.append((timestamp, frame_data_list[idx][0]))
                    frame_timestamps.append({
                        "timestamp": timestamp,
                        "frame_path": None  
                    })
                prev_hist = new_hist

            frame_data_list = []
            frame_count += 1
            pbar.update(1)

    cap.release()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    for idx, (timestamp, frame) in enumerate(extracted_frames):
        output_image_path = os.path.join(output_folder, f'frame_{idx + 1}.png')
        cv2.imwrite(output_image_path, frame)
        frame_timestamps[idx]["frame_path"] = output_image_path  

    with open(json_output_path, 'w') as json_file:
        json.dump(frame_timestamps, json_file, indent=4)

    total_elapsed_time = time.time() - start_time
    
    return output_folder, json_output_path

def save_frame_from_json(json_file, video_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(json_file, 'r') as f:
        data = json.load(f)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    for page, info in data.items():
        timestamp = info['timestamp']
        frame_number = int(timestamp * fps)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()

        if ret:
            output_path = os.path.join(output_folder, page)
            cv2.imwrite(output_path, frame)
            print(f"Frame for {page} saved at {output_path}")
        else:
            print(f"Error: Unable to retrieve frame for {page}")

    cap.release()
    print(f"All frames saved to {output_folder}")

# if __name__ == "__main__":
#     json_file = './test_output/matches/page_frame_timestamps_real.json'  
#     video_path = "./test_input/test.mp4"  
#     output_folder = "./test_output/matches/frames_output"  

#     save_frame_from_json(json_file, video_path, output_folder)
    
    
    