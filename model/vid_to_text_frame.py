import os
import json
from moviepy.editor import AudioFileClip
from openai import OpenAI
from dotenv import load_dotenv

MAX_CHUNK_SIZE = 20 * 1024 * 1024

def transcribe_audio_chunk(audio_chunk_path):
    with open(audio_chunk_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    return transcription

def split_audio_by_timestamps(audio_path, timestamps_json_path, output_folder):
    with open(timestamps_json_path, 'r') as f:
        timestamps_data = json.load(f)
    
    audio_clip = AudioFileClip(audio_path)
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    chunk_info = {}
    
    sorted_pages = sorted(timestamps_data.items(), key=lambda x: float(x[1]['timestamp']))
    print(sorted_pages)
    
    for i, (page, page_info) in enumerate(sorted_pages):
        start_timestamp = float(page_info['timestamp'])
        
        if i < len(sorted_pages) - 1:
            end_timestamp = float(sorted_pages[i + 1][1]['timestamp']) - 1
        else:
            end_timestamp = audio_clip.duration
        
        audio_chunk = audio_clip.subclip(start_timestamp, end_timestamp)
        
        audio_chunk_path = os.path.join(output_folder, f"{page}_chunk.mp3")
        audio_chunk.write_audiofile(audio_chunk_path, codec="mp3")
        
        chunk_info[page] = {
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            "audio_chunk_path": audio_chunk_path
        }
    
    audio_clip.close()
    
    chunk_info_path = os.path.join(output_folder, "chunk_info.json")
    with open(chunk_info_path, 'w') as f:
        json.dump(chunk_info, f, indent=4)
    
    return chunk_info_path

# NOT WORKING WITH FILES LARGER THAN 25MB
# def transcribe_chunks(chunk_info_path):
#     with open(chunk_info_path, 'r') as f:
#         chunk_info = json.load(f)
    
#     transcriptions = {}
    
#     for page, info in chunk_info.items():
#         print(f"Transcribing chunk for {page}...")
#         transcription_text = transcribe_audio_chunk(info['audio_chunk_path'])
#         transcriptions[page] = {
#             "start_timestamp": info['start_timestamp'],
#             "end_timestamp": info['end_timestamp'],
#             "text": transcription_text,
#             "audio_chunk_path": info['audio_chunk_path']
#         }
#     return transcriptions

def split_large_audio(audio_path, max_size=MAX_CHUNK_SIZE):
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    file_size = os.path.getsize(audio_path)
    chunk_duration = (max_size / file_size) * duration
    
    chunks = []
    for start in range(0, int(duration), int(chunk_duration)):
        end = min(start + chunk_duration, duration)
        chunk = audio.subclip(start, end)
        chunk_path = f"{audio_path}_chunk_{start}.mp3"
        chunk.write_audiofile(chunk_path, codec='mp3')
        chunks.append(chunk_path)
    
    audio.close()
    return chunks

def transcribe_chunks(chunk_info_path):
    with open(chunk_info_path, 'r') as f:
        chunk_info = json.load(f)
    
    transcriptions = {}
    
    for page, info in chunk_info.items():
        print(f"Processing chunk for {page}...")
        audio_path = info['audio_chunk_path']
        file_size = os.path.getsize(audio_path)
        
        if file_size > MAX_CHUNK_SIZE:
            print(f"  Chunk size ({file_size / 1024 / 1024:.2f}MB) exceeds 20MB. Splitting into smaller chunks...")
            sub_chunks = split_large_audio(audio_path)
            sub_transcriptions = []
            
            for i, sub_chunk in enumerate(sub_chunks):
                print(f"  Transcribing sub-chunk {i+1}/{len(sub_chunks)}...")
                sub_transcription = transcribe_audio_chunk(sub_chunk)
                sub_transcriptions.append(sub_transcription)
                os.remove(sub_chunk)  
            
            transcription_text = " ".join(sub_transcriptions)
        else:
            print(f"  Transcribing chunk (size: {file_size / 1024 / 1024:.2f}MB)...")
            transcription_text = transcribe_audio_chunk(audio_path)
        
        transcriptions[page] = {
            "start_timestamp": info['start_timestamp'],
            "end_timestamp": info['end_timestamp'],
            "text": transcription_text,
            "audio_chunk_path": audio_path
        }
    
    return transcriptions

def process_audio_and_generate_json(audio_path, timestamps_json_path, output_json_path, chunk_output_folder):
    print("Splitting audio into chunks...")
    chunk_info_path = split_audio_by_timestamps(audio_path, timestamps_json_path, chunk_output_folder)
    
    print("Chunking completed. Chunk info saved to:", chunk_info_path)
    
    print("Starting transcription process...")
    transcriptions = transcribe_chunks(chunk_info_path)
    
    print("Writing transcriptions to JSON...")
    with open(output_json_path, 'w') as outfile:
        json.dump(transcriptions, outfile, indent=4)
    
    print("Process completed successfully!")

if __name__ == "__main__":
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    audio_path = "./test_input/output_audio.mp3"
    timestamps_json_path = './test_output/matches/page_frame_timestamps_real.json'
    output_json_path = "./test_output/segmented_transcriptions.json"
    chunk_output_folder = "./test_output/matches/audio_chunks"
    
    process_audio_and_generate_json(audio_path, timestamps_json_path, output_json_path, chunk_output_folder)