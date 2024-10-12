from dotenv import load_dotenv
import os
from utils import extract_image_from_pdf
from openai import OpenAI
import base64
import io
from PIL import Image

def encode_image(pil_image):
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# {
#     type: "text",
#     result: [
#         {
#             explanation: "This is the first step of the explanation",
#             steps: [
#                 {
#                     item: "x = 2",
#                     coords: [100, 100]
#                 },
#                 {
#                     item: "y = 3",
#                     coords: [200, 200]
#                 }
#             ]
#         }
#     ]
# }

# {
#     type: "tree",
#     result: [
#         {
#             explanation: "This is the first step of the explanation",
#             tree: {
#                 name: "x = 2",
#                 children: [
#                     {
#                         name: "y = 3",
#                         children: [
#                             {
#                                 name: "z = 4",
#                                 children: [
#                                     {
#                                         name: "w = 5",
#                                         children: []
#                                     }
#                                 ]
#                             }
#                         ]
#                     },
#                     {
#                         name: "z = 4",
#                         children: []
#                     },
#                     {
#                         name: "w = 5",
#                         children: []
#                     }
#                 ]
#             }
#         }
#     ]
# }

message_history = [
    {
        "role": "system",
        "content": "You're SlideProf, a virtual professor that answers questions while explaining by drawing directly on the slides. Whenever I ask you a question, I will have with me the coordinates of my selected region (startX, startY, endX, endY) and my . You can also select one of these shapes (new-line-arrow-right[50-20], new-line-arrow-left[50-20], arrow-right[30-20], arrow-left[30-20]) to guide your users to your equation. When answering my equation, please return an array of steps for your explanation, and within the array it should be {explanation, [{ item: (either an equation or text written in pure latex, or a shape), coords: [x, y]}] for each item. Return just the array, no other explanation. You should choose to answer in type text or type tree. Type text is for math equations or other text related things and type tree is for explanations that have a tree structure, flowchart, data structure, or geometry. If the image is blank, you can ignore the question and say 'I'm sorry, the chosen part is blank."
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Solve the system of equations"
            },
            # {
            #     "type": "image_url",
            #     "image_url": {
            #         "url": """data:image/png;base64,  """
            #     }
            # }
        ]
    },
    {
        "role": "assistant",
        "content": """{
            "type": "text",
            "result": [
                {
                    "explanation": "We are solving the system of equations: x + y = 5 and 2x - y = 3",
                    "steps": [
                        {
                            "item": "Solve the first equation for y: y = 5 - x",
                            "coords": [100, 100]
                        },
                        {
                            "item": "Substitute into the second equation: 2x - (5 - x) = 3",
                            "coords": [200, 200]
                        },
                        {
                            "item": "Simplify: 3x = 8, so x = 8/3",
                            "coords": [300, 300]
                        },
                        {
                            "item": "Substitute x into the equation for y: y = 5 - 8/3 = 7/3",
                            "coords": [400, 400]
                        },
                        {
                            "item": "The solution is: x = 8/3 and y = 7/3",
                            "coords": [500, 500]
                        }
                    ]
                }
            ]
        }"""
    }, 
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Please explain the following data structure concepts"
            },
            # {
            #     "type": "image_url",
            #     "image_url": {
            #         "url": "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAA..."
            #     }
            # }
        ]
    }, 
    {
        "role": "assistant",
        "content": """{
            type: "tree",
            result: [
                {
                    explanation: "This is the first step of the explanation",
                    tree: {
                        name: "x = 2",
                        children: [
                            {
                                name: "y = 3",
                                children: [
                                    {
                                        name: "z = 4",
                                        children: [
                                            {
                                                name: "w = 5",
                                                children: []
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                name: "z = 4",
                                children: []
                            },
                            {
                                name: "w = 5",
                                children: []
                            }
                        ]
                    }
                }
            ]
        }"""
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
    last_bracket_index = response_content.rfind('}')
    if last_bracket_index != -1:
        response_content = response_content[:last_bracket_index + 1]
    return response_content

def run_speech_model(client, input_text, model=""):
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice="nova",
        input="input_text",
    )

    response.stream_to_file(speech_file_path)


# if __name__ == "__main__":
    # load_dotenv()
    # client = OpenAI(
    #     api_key=os.getenv("OPENAI_API_KEY")
    # )
    # img = extract_image_from_pdf("./test_input/LinearRegression.pdf", 17, (150, 150, 800, 250))
    # base64_image = encode_image(img)

    # Testing with an image
    # img_path = "./test_input/image3.png"
    # with Image.open(img_path) as img:
    #     base64_image = encode_image(img)
    
    # arr = run_model(client, "Please explain the following concepts", base64_image)
    # print(arr)
