from dotenv import load_dotenv
import os
from utils import extract_text_from_pdf
from openai import OpenAI
import base64
import requests

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

message_history = [
    {
    "role": "system",
    "content": "You are an AI assistant skilled in explaining technical concepts and generating LaTeX code. You should explain the requested concepts step by step, returning each step as an item in an array. The array must be normal type of array in Python, begin with [ and end with ]. Each item must be seperated by ,.  Each step must be written in proper LaTeX syntax (not markdown), and the array should contain only these LaTeX steps. Do not generate anything other than the LaTeX steps in the array. You should never give any comment. You should never generate anything after the end of the array."
    } 
]

def run_model(client, input_text, input_img, model="gpt-4o-mini"):
    message_history.append({"role": "user", "content": [
            {
            "type": "text",
            "text": input_text
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{input_img}"
            }
            }
        ]})
    
    stream = client.chat.completions.create(
        model=model,
        messages=message_history,
        stream=True,
    )
    
    response_content = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            response_content += chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content, end="")
    
    message_history.append({"role": "assistant", "content": response_content})
    last_bracket_index = response_content.rfind(']')
    if last_bracket_index != -1:
        response_content = response_content[:last_bracket_index + 1]
    return response_content

if __name__ == "__main__":
    image_path = "./test_input/image.png"
    base64_image = encode_image(image_path)
    arr = run_model(client, "Please explain the following concepts", base64_image)
    print(arr)
