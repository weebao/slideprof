import cv2
import numpy as np

def count_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return total_frames

def calculate_fps(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps

def p_hash(image_path, hash_size=8):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (32, 32))
    dct = cv2.dct(np.float32(resized))
    dct_low_freq = dct[:hash_size, :hash_size]
    dct_mean = np.mean(dct_low_freq[1:]) 
    hash_array = dct_low_freq > dct_mean
    image_hash = ''.join(['1' if val else '0' for val in hash_array.flatten()])

    return image_hash
if __name__ == '__main__':
    video_path = "test_input/test.mp4"
    print(count_frames(video_path))
    print(calculate_fps(video_path))
    print(p_hash("test_input/pages/page_1.png"))