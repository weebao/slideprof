import os
import json
from utils import extract_pages_from_pdf, mp4_to_voice
from frame_check_DL import process_video_and_pages
from vid_to_text_frame import process_audio_and_generate_json
from text_to_summary import process_json, save_json, load_json
from sum_to_pdf import merge_pdf_with_summaries

def all_to_pdf_main(client, video_path = "./test_input/test.mp4", pdf_path = "./test_input/test.pdf", pages_folder = "./test_input/pages", output_pdf_path = "./test_output", interval=1, threshold=0.85, audio_output_path = "./test_input/output_audio.mp3", timestamp_output_path = "./test_output/page_frame_timestamps.json", trans_output_path = "./test_output/segmented_transcriptions.json", chunks_folder = "./test_output/chunks", summary_output_path = "./test_output/segmented_transcriptions_with_summaries.json", final_pdf_path = "./test_output/modified_pdf_file.pdf"):
    mp4_to_voice(video_path)
    extract_pages_from_pdf(pdf_path, pages_folder)
    process_video_and_pages(video_path, pages_folder, interval, threshold, output_file=timestamp_output_path)
    
    process_audio_and_generate_json(audio_output_path, timestamps_json_path, trans_output_path, chunks_folder)
    data = load_json(trans_output_path)
    processed_data = process_json(client, data, pages_folder)
    save_json(processed_data, summary_output_path)
    
    data = load_json(summary_output_path)
    merge_pdf_with_summaries(pdf_path, data, final_pdf_path)
    