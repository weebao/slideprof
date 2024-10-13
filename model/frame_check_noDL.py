import cv2
import os
import json
import time
from skimage.metrics import structural_similarity as ssim
import imagehash
from PIL import Image
from tqdm import tqdm
import numpy as np
import multiprocessing

def calculate_ssim(imageA, imageB):
    imageA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    imageB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    if imageA.shape != imageB.shape:
        imageB = cv2.resize(imageB, (imageA.shape[1], imageA.shape[0]))
    score, _ = ssim(imageA, imageB, full=True)
    return score

def compare_hash(imageA, imageB):
    hashA = imagehash.average_hash(Image.fromarray(cv2.cvtColor(imageA, cv2.COLOR_BGR2RGB)))
    hashB = imagehash.average_hash(Image.fromarray(cv2.cvtColor(imageB, cv2.COLOR_BGR2RGB)))
    hash_diff = hashA - hashB  
    return hash_diff

def match_pages_ssim(video_path, pages_folder, output_folder, n=2, ssim_threshold=0.9):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    page_files = sorted(os.listdir(pages_folder))
    page_count = 0
    total_pages = len(page_files)

    frame_count = 0
    matched_data_ssim = []

    delay_frames = int(fps * n) if n > 0 else 1 
    
    with tqdm(total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), desc="Processing frames (SSIM)", position=0, leave=True) as pbar:
        while cap.isOpened() and page_count < total_pages:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % delay_frames != 0:
                frame_count += 1
                pbar.update(1)
                continue

            current_page_path = os.path.join(pages_folder, page_files[page_count])
            page_image = cv2.imread(current_page_path)

            # Apply SSIM comparison
            ssim_score = calculate_ssim(page_image, frame)
            if ssim_score > ssim_threshold:
                timestamp = frame_count / fps
                matched_data_ssim.append({
                    "page": page_files[page_count],
                    "frame_number": frame_count,
                    "timestamp": timestamp,
                    "ssim_score": ssim_score
                })

            if ssim_score > ssim_threshold:
                page_count += 1

            frame_count += 1
            pbar.update(1)

    cap.release()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(os.path.join(output_folder, 'ssim_matches.json'), 'w') as json_file:
        json.dump(matched_data_ssim, json_file, indent=4)

    return os.path.join(output_folder, 'ssim_matches.json')


def match_pages_hash(video_path, pages_folder, output_folder, n=2, hash_threshold=10):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    page_files = sorted(os.listdir(pages_folder))
    page_count = 0
    total_pages = len(page_files)

    frame_count = 0
    matched_data_hash = []

    delay_frames = int(fps * n) if n > 0 else 1  
    
    with tqdm(total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), desc="Processing frames (Hash)", position=1, leave=True) as pbar:
        while cap.isOpened() and page_count < total_pages:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % delay_frames != 0:
                frame_count += 1
                pbar.update(1)
                continue

            current_page_path = os.path.join(pages_folder, page_files[page_count])
            page_image = cv2.imread(current_page_path)

            hash_diff = compare_hash(page_image, frame)
            if hash_diff < hash_threshold:  
                timestamp = frame_count / fps
                matched_data_hash.append({
                    "page": page_files[page_count],
                    "frame_number": frame_count,
                    "timestamp": timestamp,
                    "hash_difference": hash_diff
                })

            if hash_diff < hash_threshold:
                page_count += 1

            frame_count += 1
            pbar.update(1)

    cap.release()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(os.path.join(output_folder, 'hash_matches.json'), 'w') as json_file:
        json.dump(matched_data_hash, json_file, indent=4)

    return os.path.join(output_folder, 'hash_matches.json')


if __name__ == "__main__":
    video_path = "./test_input/test.mp4" 
    pages_folder = "./test_input/pages"  
    output_folder = "./test_output/matches"  

    ssim_process = multiprocessing.Process(target=match_pages_ssim, args=(video_path, pages_folder, output_folder, 0, 0.9))
    hash_process = multiprocessing.Process(target=match_pages_hash, args=(video_path, pages_folder, output_folder, 0, 10))

    ssim_process.start()
    hash_process.start()

    ssim_process.join()
    hash_process.join()

    print("Processing complete!")
