from dotenv import load_dotenv
import os
from utils import extract_image_from_pdf
from openai import OpenAI
import base64
import io

def encode_image(pil_image):
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

message_history = [
    {
    "role": "system",
    "content": "You're SlideProf, a virtual professor that answers questions while explaining by drawing directly on the slides. Whenever I ask you a question, I will have with me the coordinates of my selected region (startX, startY, endX, endY) and my . You can also select one of these shapes (new-line-arrow-right[50-20], new-line-arrow-left[50-20], arrow-right[30-20], arrow-left[30-20]) to guide your users to your equation. When answering my equation, please return an array of steps for your explanation, and within the array it should be {explanation, [{ item: (either an equation or text written in pure latex, or a shape), coords: [x, y]}] for each item. Return just the array, no other explanation. For questions unrelated to the content of the slide, do not answer them and only answer about contents of the slide. "
    } 
    # {
    # "role": "system",
    # "content": "You are an AI assistant skilled in explaining technical concepts and generating LaTeX code. You should explain the requested concepts step by step, returning each step as an item in an array. The array must be normal type of array in Python, begin with [ and end with ]. Each item must be seperated by ,.  Each step must be written in proper LaTeX syntax (not markdown), and the array should contain only these LaTeX steps. Do not generate anything other than the LaTeX steps in the array. You should never give any comment. You should never generate anything after the end of the array."
    # } 
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
    img = extract_image_from_pdf("./test_input/LinearRegression.pdf", 17, (150, 150, 800, 250))
    # img.show()
    base64_image = encode_image(img)
    arr = run_model(client, "Please explain the following concepts", base64_image)
    # print(arr)
