import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import base64
import io

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def estimate_token_count(text):
    return len(text) // 4

def encode_image(image_path):
    with Image.open(image_path) as img:
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

def generate_summary(text, image_path, model = "gpt-4o"):
    system_prompt = """
    Generate concise summaries from text that complement or explain the associated visual content. The summaries should be suitable for display in a PowerPoint slide or PDF file.

    - Focus on key points that enhance the understanding of the image.
    - You should never repeat the same thing from the image. No need to describe the main object of the course. 
    - You don't need to give the name of the author or the course name.
    - Use bullet points for each key point.
    - Ensure lines end clearly for aesthetically pleasing display.

    # Steps

    1. Analyze the text and identify key details or themes that relate to the visual content.
    2. Determine which aspects of the text best complement or enhance the understanding of the image.
    3. Craft concise bullet points summarizing these key aspects.
    4. Format bullet points with clear line endings for readability.

    # Output Format

    - Bullet points
    - Clear sentence endings appropriate for presentation format (PowerPoint or PDF)
    - Concise and easy to understand

    # Examples

    **Input Text:** 
    "The report highlights the quarterly increase in sales by 15%, with significant growth in the electronics sector. Compared to the previous quarter, there is a noticeable improvement in marketing strategies leading to better consumer engagement."

    **Associated Image:** 
    An upward-trending sales graph related to the electronics sector.

    **Output:**
    - Sales increased by 15% this quarter.
    - Electronics sector shows significant growth.
    - Improved marketing strategies boost consumer engagement.

    (Note: Real outputs should be concise with clear, aesthetically pleasing line endings suitable for presentations.)
    """

    encoded_image = encode_image(image_path)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Generate a summary for the following text, considering the content of the associated image:\n\n{text}"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content

def process_json(data, img_folder, token_limit=0):
    for page, details in data.items():
        print(f"Processing page {page}")
        text = details.get('text', "")
        token_count = estimate_token_count(text)
        
        img_path = os.path.join(img_folder, f"{page}") 
        
        if token_count > token_limit or os.path.exists(img_path):
            summary = generate_summary(text, img_path)
            data[page]['summary'] = summary
        else:
            data[page]['summary'] = text
        print(f"Summary generated for {page}")
    return data

if __name__ == "__main__":
    load_dotenv()
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    input_file = './test_output/segmented_transcriptions.json'
    output_file = './test_output/segmented_transcriptions_with_summaries.json'
    img_folder = './test_input/pages'

    data = load_json(input_file)
    processed_data = process_json(data, img_folder)
    save_json(processed_data, output_file)
    print(f"Updated file saved at {output_file}")