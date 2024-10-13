import logging
import torch
import torchvision.transforms as transforms
from torchvision import models
import cv2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
from torch.utils.data import DataLoader, Dataset
import os
import json
from tqdm import tqdm
import natsort  # Import natsort for natural sorting

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = models.efficientnet_b2(pretrained=True)
model = torch.nn.Sequential(*list(model.children())[:-1]).to(device)
model.eval()

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

class ImageDataset(Dataset):
    def __init__(self, image_paths):
        self.image_paths = image_paths

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        img = Image.open(img_path).convert('RGB')
        img_tensor = preprocess(img)
        return img_tensor, img_path

def extract_features_batch(model, data_loader):
    features = []
    image_paths = []
    with torch.no_grad():
        for imgs, paths in tqdm(data_loader, desc="Processing pages"):
            imgs = imgs.to(device)
            output = model(imgs)
            output = output.squeeze(-1).squeeze(-1).cpu().numpy()
            features.extend(output)
            image_paths.extend(paths)
    return np.array(features), image_paths

def extract_single_feature(model, frame):
    with torch.no_grad():
        frame_tensor = preprocess(frame).unsqueeze(0).to(device)
        embedding = model(frame_tensor).squeeze().cpu().numpy()
    return embedding

def extract_video_frames(video_path, interval=2):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    embeddings = []
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    with tqdm(total=total_frames, desc="Processing video frames") as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame_rgb)
                embedding = extract_single_feature(model, frame_pil)
                timestamp = frame_count / fps
                embeddings.append((timestamp, embedding))

            frame_count += 1
            pbar.update(1)

    cap.release()
    return embeddings

def save_results_to_json(page_paths, timestamps, output_file):
    print("Saving results...")
    results = {os.path.basename(page_paths[i]): {"timestamp": timestamps[i]} for i in range(len(page_paths))}
    with open(output_file, 'w') as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Results saved to {output_file}")

def match_pages_to_frames(page_embeddings, frame_embeddings, threshold=0.85):
    timestamps = [0.0]

    start_frame = 0

    for page_idx in range(1, len(page_embeddings)):
        page_embedding = page_embeddings[page_idx]
        for frame_idx in range(start_frame, len(frame_embeddings)):
            timestamp, frame_embedding = frame_embeddings[frame_idx]
            similarity = cosine_similarity([page_embedding], [frame_embedding])[0][0]
            if similarity >= threshold:
                timestamps.append(timestamp)
                print(f"Page {page_idx + 1} matched to frame {frame_idx} with similarity {similarity}")
                start_frame = frame_idx + 1  
                print(f"Start frame updated to {start_frame}")
                break

    return timestamps

def process_video_and_pages(video_path, pages_folder, interval=2, threshold=0.85):
    image_paths = [os.path.join(pages_folder, f) for f in os.listdir(pages_folder) if f.endswith(('.jpg', '.png'))]
    
    image_paths = natsort.natsorted(image_paths)

    image_dataset = ImageDataset(image_paths)
    data_loader = DataLoader(image_dataset, batch_size=8, shuffle=False)

    print("Extracting embeddings for pages...")
    page_embeddings, page_paths = extract_features_batch(model, data_loader)

    print(f"Extracting embeddings for video frames every {interval} seconds...")
    frame_embeddings = extract_video_frames(video_path, interval=interval)

    print("Matching pages to frames...")
    timestamps = match_pages_to_frames(page_embeddings, frame_embeddings, threshold)

    save_results_to_json(page_paths, timestamps, 'page_frame_timestamps.json')

if __name__ == "__main__":
    video_path = "/content/drive/MyDrive/HackHarvard/test.mp4"  
    pages_folder = "/content/drive/MyDrive/HackHarvard/pages"  
    interval = 1
    threshold = 0.85  

    process_video_and_pages(video_path, pages_folder, interval, threshold)
