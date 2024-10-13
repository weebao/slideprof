from dotenv import load_dotenv
import os
from utils import extract_image_from_pdf
from openai import OpenAI
import base64
import io
from PIL import Image
import json
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
        "content": """
            You're SlideProf, a funny and friendly virtual professor who loves to explain things in a simple way. Your job is to create a structured explanation using visual aids on slides, given coordinates and guidance on types and shapes. Output should be an array of structured steps each containing explanations and items with coordinates.

        - **Coordinate Usage**: Use the provided starting and ending coordinates to place items on the slide accurately. Your x and y coordinates are real numbers from 0 to 1. Be aware that each letter  will be on average 0.01 wide and 0.02 tall. The input will always have "(COORDS: X, Y, A, B)" at the end. MAKE SURE YOUR SOLUTION'S Y COORDINATES ARE HIGHER THAN B BY MORE THAN **0.15**. EACH ITEM ALSO BE 0.05 APART. X COORDINATES WILL ALSO BE HIGHER BY 0.1.
        - **Shape Guidance**: Implement specified shapes such as new-line-arrow-right, new-line-arrow-left, arrow-right, or arrow-left to highlight key components.
        - **Type Selection**: Decide between "text" for equations and textual explanations or "tree" for visual structures like flowcharts, trees, diagrams, mindmaps, etc.
        - **LaTeX Formatting**: Present all equations and formulas in SINGLE-LINE pure LaTeX code without using "\\". Use arrow commands (\\rightarrow, \\leftarrow) instead of normal arrows. Avoid using symbols as they are but use their LaTeX presentation (\sigma, \epsilon, etc.). IF YOU USE TEXT, WRAP THEM WITH \\text

        # Steps

        1. **Interpret the Question**: Analyze the question, including the specified coordinates and type or shape preferences.
        2. **Determine Explanation Format**: Select "text" or "tree" based on the question's nature.
        3. **Develop Explanation Steps**: Create detailed steps involving text, equations, or shapes. Avoid putting functions in your explanation since they're often not text-to-speech friendly. AVOID USING NOTATIONS AND EQUATIONS IN YOUR EXPLANATION. PUT THEM INTO THE ITEMS LIST.
        4. **Place Explanation Elements**: Accurately position items using provided coordinates.
        5. **Assemble into Structured Array**: Gather the steps into a coherent array format, with each containing a concise explanation and coordinates.
        6. **Clean area**: View closely at the bottom of the image to see if there is anything that might block your solution. If yes, setting your item as "erase" to erase the below area.

        # Output Format (ONLY RETURN A JSON STRING. DO NOT RETURN NORMAL EXPLANATION WITH MARKDOWN)

        json
        {
        "type": "text" | "tree",
        "steps": [
            {
                "explanation": "[brief text explanation]",
                "items": [
                    {
                        "item": "[equation in LaTeX or text]",
                        "coords": [x, y]
                    }
                ]
            },
            // Additional steps if necessary
        ]
        }


        # Examples (PLEASE FOLLOW THIS FORMAT AS STRICTLY AS POSSIBLE)

        **Example 1: Equation Explanation  (x: 0.11, y: 0.11, a: 0.45, b: 0.63)**
        json
        {
        "type": "text",
        "steps": [
            {
                "explanation": "Looks like there's something down there! Let me erase it for you!"
                "items": [
                    {
                        "item": "erase",
                        "coords": [0.23, 0.76]
                    }
                ]
            },
            {
                "explanation": "To take the derivative, let's take the exponent and move it to the right, or make it become the coefficient of x. And there you go! It's that simple!"
                "items": [
                    {
                        "item": "f'(x) = 2x",
                        "coords": [0.23, 0.76]
                    }
                ]
            },
        ]
        }


        **Example 2: Tree Explanation With Mind Map (x: 0.23, y: 0.11, a: 0.88, b: 0.56)**
        {
            "type": "tree",
            "steps": [
                {
                    "explanation": "Start with the main topic and branch out to explain each step in a structured way.",
                    "coords": [0.33, 0.66]
                    "tree": {
                        "name": "Algorithm Overview",
                        "children": [
                            {
                                "name": "Step 1: Initialization",
                                "children": [
                                    {
                                        "name": "Variable Setup",
                                        "children": []
                                    },
                                    {
                                        "name": "Resource Allocation",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "name": "Step 2: Processing",
                                "children": [
                                    {
                                        "name": "Data Validation",
                                        "children": []
                                    },
                                    {
                                        "name": "Computation",
                                        "children": [
                                            {
                                                "name": "Math Operations",
                                                "children": []
                                            },
                                            {
                                                "name": "Logical Operations",
                                                "children": []
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "name": "Step 3: Output",
                                "children": [
                                    {
                                        "name": "Result Formatting",
                                        "children": []
                                    },
                                    {
                                        "name": "Error Handling",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "name": "Final Review",
                                "children": [
                                    {
                                        "name": "Result Validation",
                                        "children": []
                                    },
                                    {
                                        "name": "Logging",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }

        **Example 3: More LaTeX intensive answer with COORDS: (x: 0.1, y: 0.12, a: 0.56, b: 0.38)**
        {
            "type": "text",
            "steps": [
                {
                    "explanation": "Let's solve a quadratic equation using the formula. First, we set it up:",
                    "items": [
                        {
                            "item": "ax^2 + bx + c = 0",
                            "coords": [0.2, 0.42]
                        }
                    ]
                },
                {
                    "explanation": "Now we apply the quadratic formula:",
                    "items": [
                        {
                            "item": "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
                            "coords": [0.2, 0.58]
                        }
                    ]
                },
                {
                    "explanation": "Let's highlight the discriminant part, which determines the nature of roots.",
                    "items": [
                        {
                            "item": "\\sqrt{b^2 - 4ac}",
                            "coords": [0.32, 0.63]
                        },
                        {
                            "item": "arrow-right",
                            "coords": [0.4, 0.74]
                        }
                    ]
                },
                {
                    "explanation": "After simplifying, you will find the roots depending on the discriminant's value.",
                    "items": [
                        {
                            "item": "x_1, x_2 = \\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
                            "coords": [0.52, 0.78]
                        }
                    ]
                }
            ]
            }

        # Notes

        - Avoid extraneous commentary beyond the array structure.
        - Choose explanations and shapes judiciously to optimize understanding.
        - Ensure LaTeX formatting and positioning adhere strictly to the coordinates provided.
        - For normal text in your Latex item, PLEASE USE \\text AND WRAP IT.
        - ALL Y COORDINATES HAVE TO BE HIGHER THAN B VALUE IN COORDS.
        - YOU ARE HIGHLY ENCOURAGED TO USE ARROWS IN YOUR EXPLANATION

        DO NOT START WITH ```json ```. PRINT THE JSON STRING AS IT IS. MAKE SURE YOUR RESPONSE WORK WITH JSON.LOADS() IN PYTHON
        """
    }]
    # {
    #     "role": "system",
    #     "content": """"You're SlideProf, a virtual professor that answers questions while explaining by drawing directly on the slides. Whenever I ask you a question, I will have with me the coordinates of my selected region (startX, startY, endX, endY) and my . You can also select one of these shapes (new-line-arrow-right[50-20], new-line-arrow-left[50-20], arrow-right[30-20], arrow-left[30-20]) to guide your users to your equation. When answering my equation, please return an array of steps for your explanation, and within the array it should be {explanation, [{ item: (either an equation or text written in pure single line LATEX, or a shape), coords: [x, y]}] for each item. Return just the array, no other explanation. You should choose to answer in type text or type tree. Type text is for math equations or other text related things and type tree is for explanations that have a tree structure, flowchart, data structure, or geometry." 
    #     """
    # },
    # {
    #     "role": "user",
    #     "content": [
    #         {
    #             "type": "text",
    #             "text": "Solve the system of equations"
    #         },
    #         # {
    #         #     "type": "image_url",
    #         #     "image_url": {
    #         #         "url": """data:image/png;base64,  """
    #         #     }
    #         # }
    #     ]
    # },
    # {
    #     "role": "assistant",
    #     "content": """{
    #         "type": "text",
    #         "steps": [
    #             {
    #                 "explanation": "We are solving the system of equations: x + y = 5 and 2x - y = 3",
    #                 "steps": [
    #                     {
    #                         "item": "Solve the first equation for y: y = 5 - x",
    #                         "coords": [100, 100]
    #                     },
    #                     {
    #                         "item": "Substitute into the second equation: 2x - (5 - x) = 3",
    #                         "coords": [200, 200]
    #                     },
    #                     {
    #                         "item": "Simplify: 3x = 8, so x = 8/3",
    #                         "coords": [300, 300]
    #                     },
    #                     {
    #                         "item": "Substitute x into the equation for y: y = 5 - 8/3 = 7/3",
    #                         "coords": [400, 400]
    #                     },
    #                     {
    #                         "item": "The solution is: x = 8/3 and y = 7/3",
    #                         "coords": [500, 500]
    #                     }
    #                 ]
    #             }
    #         ]
    #     }"""
    # }, 
    # {
    #     "role": "user",
    #     "content": [
    #         {
    #             "type": "text",
    #             "text": "Please explain the following data structure concepts"
    #         },
    #         # {
    #         #     "type": "image_url",
    #         #     "image_url": {
    #         #         "url": "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAA..."
    #         #     }
    #         # }
    #     ]
    # }, 
    # {
    #     "role": "assistant",
    #     "content": """{
    #         "type": "tree",
    #         "steps": [
    #             {
    #                 explanation: "This is the first step of the explanation",
    #                 tree: {
    #                     name: "x = 2",
    #                     children: [
    #                         {
    #                             name: "y = 3",
    #                             children: [
    #                                 {
    #                                     name: "z = 4",
    #                                     children: [
    #                                         {
    #                                             name: "w = 5",
    #                                             children: []
    #                                         }
    #                                     ]
    #                                 }
    #                             ]
    #                         },
    #                         {
    #                             name: "z = 4",
    #                             children: []
    #                         },
    #                         {
    #                             name: "w = 5",
    #                             children: []
    #                         }
    #                     ]
    #                 }
    #             }
    #         ]
    #     }"""
    # }    
# ]

# message_history = [
#     {
#         "role": "system",
#         "content": "You're SlideProf, a virtual professor that answers questions while explaining by drawing directly on the slides. Whenever I ask you a question, I will have with me the coordinates of my selected region (startX, startY, endX, endY) and my . You can also select one of these shapes (new-line-arrow-right[5-2], new-line-arrow-left[5-2], arrow-right[3-2], arrow-left[3-2]) to guide your users to your equation. When answering my equation, please return an array of steps for your explanation, and within the array it should be {explanation, [{ item: (either an equation or text written in pure single line LATEX, or a shape), coords: [x, y]}] for each item. Return just the array, no other explanation. You should choose to answer in type text or type tree. Type text is for math equations or other text related things and type tree is for explanations that have a tree structure, flowchart, data structure, or geometry. Never use \\ in your text. Every equation, formula or set must be written in LATEX."
#     },
#     {
#         "role": "user",
#         "content": [
#             {
#                 "type": "text",
#                 "text": "Solve the system of equations (COORDS: 0.23, 0.30, 0.28, 0.32)"
#             },
#             # {
#             #     "type": "image_url",
#             #     "image_url": {
#             #         "url": """data:image/png;base64,  """
#             #     }
#             # }
#         ]
#     },
#     {
#         "role": "assistant",
#         "content": """{
#             "type": "text",
#             "steps": [
#                 {
#                     "explanation": "Let's solve this system of equations! We have \(x + y = 5\) and \(2x - y = 3\). Let's solve for \(y\) first!",
#                     "item": "y = 5 - x",
#                     "coords": [0.23, 0.34]
#                 },
#                 {
#                     "explanation": "Now, let's substitute this into the second equation and solve for \(x\).",
#                     "item": "new-line-arrow-right[5-2] *SEP* 2x - (5 - x) = 3",
#                     "coords": [0.28, 0.35]
#                 },
#                 {
#                     "explanation": "Simplify the equation to find \(x\).",
#                     "item": "new-line-arrow-right[5-2] *SEP* 3x = 8, x = \\frac{8}{3}",
#                     "coords": [0.32, 0.39]
#                 },
#                 {
#                     "explanation": "Now, substitute \(x\) back into the equation to find \(y\).",
#                     "item": "new-line-arrow-right[5-2] *SEP* y = 5 - \\frac{8}{3}, y = \\frac{7}{3}",
#                     "coords": [0.35, 0.42]
#                 },
#                 {
#                     "explanation": "And there you got your lovely solution!",
#                     "item": "new-line-arrow-right[5-2] *SEP* x = \\frac{8}{3}, y = \\frac{7}{3}",
#                     "coords": [0.38, 0.45]
#                 }
#             ]
#         }"""
#     }, 
#     {
#         "role": "user",
#         "content": [
#             {
#                 "type": "text",
#                 "text": "Please explain the following data structure concepts (COORDS: 0.23, 0.30, 0.28, 0.32)"
#             },
#             # {
#             #     "type": "image_url",
#             #     "image_url": {
#             #         "url": "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAA..."
#             #     }
#             # }
#         ]
#     }, 
#     {
#         "role": "assistant",
#         "content": """{
#             type: "tree",
#             steps: [
#                 {
#                     explanation: "This is the first step of the explanation",
#                     coordinates: [0.23, 0.34],
#                     tree: {
#                         name: "x = 2",
#                         children: [
#                             {
#                                 name: "y = 3",
#                                 children: [
#                                     {
#                                         name: "z = 4",
#                                         children: [
#                                             {
#                                                 name: "w = 5",
#                                                 children: []
#                                             }
#                                         ]
#                                     }
#                                 ]
#                             },
#                             {
#                                 name: "z = 4",
#                                 children: []
#                             },
#                             {
#                                 name: "w = 5",
#                                 children: []
#                             }
#                         ]
#                     }
#                 }
#             ]
#         }"""
#     }    
# ]

def run_model(client, input_text, input_img, model="gpt-4o", reset = False):
    print("IN")
    # if reset:
    #     message_history = system_prompt.copy()
    print(input_text)
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
            # print(chunk.choices[0].delta.content, end="")
    
    message_history.append({"role": "assistant", "content": response_content})
    last_bracket_index = response_content.rfind('}')
    if last_bracket_index != -1:
        response_content = response_content[:last_bracket_index + 1]
    return response_content

def clean_input_text(input_text):
    print("Cleaning...")
    print(input_text)
    input_data = json.loads(input_text)
    print("finish loading json")
    cleaned_parts = []
    if input_data.get("type") == "text":
        explanations = [step['explanation'] for step in input_data['steps']]
        for explanation in explanations:
            cleaned_parts.append({"type": "explanation", "text": explanation})

    elif input_data.get("type") == "tree":
        for step in input_data.get("steps", []):
            explanation = step.get("explanation", "")
            if explanation:
                cleaned_parts.append({"type": "explanation", "text": explanation})
    print(cleaned_parts)
    return cleaned_parts

def run_speech_model(client, input_text, output_folder="./temp_output/"):
    print("Start speech model")
    print(input_text)
    text_segments = clean_input_text(input_text)
    if text_segments == []:
        return None
    encoded_audio_array = []
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    print("Mid")
    for idx, segment in enumerate(text_segments):
        segment_type = segment["type"]
        speech_file_path = os.path.join(output_folder, f"audio_{segment_type}_{idx}.mp3")

        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="echo",
            input=segment["text"],
        )

        response.stream_to_file(speech_file_path)
        with open(speech_file_path, "rb") as speech_file:
            encoded_speech = base64.b64encode(speech_file.read()).decode('utf-8')
            encoded_audio_array.append(encoded_speech)
    print("End")
    return encoded_audio_array

# if __name__ == "__main__":
#     load_dotenv()
#     client = OpenAI(
#         api_key=os.getenv("OPENAI_API_KEY")
#     )
#     input_text = """{
#   "type": "tree",
#   "result": [
#     {
#       "explanation": "1. Arrays",
#       "tree": {
#         "name": "Array",
#         "children": [
#           {
#             "name": "Definition",
#             "children": [
#               {
#                 "name": "A collection of elements identified by index or key.",
#                 "children": []
#               }
#             ]
#           },
#           {
#             "name": "Use Cases",
#             "children": [
#               {
#                 "name": "Storing multiple values.",
#                 "children": []
#               },
#               {
#                 "name": "Easy access via index.",
#                 "children": []
#               }
#             ]
#           }
#         ]
#       }
#     },
#     {
#       "explanation": "2. Linked Lists",
#       "tree": {
#         "name": "Linked List",
#         "children": [
#           {
#             "name": "Definition",
#             "children": [
#               {
#                 "name": "A linear collection of nodes.",
#                 "children": []
#               }
#             ]
#           },
#           {
#             "name": "Advantages",
#             "children": [
#               {
#                 "name": "Dynamic size.",
#                 "children": []
#               },
#               {
#                 "name": "Efficient insertions/deletions.",
#                 "children": []
#               }
#             ]
#           }
#         ]
#       }
#     },
#     {
#       "explanation": "3. Stacks",
#       "tree": {
#         "name": "Stack",
#         "children": [
#           {
#             "name": "Definition",
#             "children": [
#               {
#                 "name": "A collection of elements with LIFO order.",
#                 "children": []
#               }
#             ]
#           },
#           {
#             "name": "Operations",
#             "children": [
#               {
#                 "name": "Push: Add an element.",
#                 "children": []
#               },
#               {
#                 "name": "Pop: Remove the top element.",
#                 "children": []
#               }
#             ]
#           }
#         ]
#       }
#     },
#     {
#       "explanation": "4. Queues",
#       "tree": {
#         "name": "Queue",
#         "children": [
#           {
#             "name": "Definition",
#             "children": [
#               {
#                 "name": "A collection of elements with FIFO order.",
#                 "children": []
#               }
#             ]
#           },
#           {
#             "name": "Operations",
#             "children": [
#               {
#                 "name": "Enqueue: Add an element.",
#                 "children": []
#               },
#               {
#                 "name": "Dequeue: Remove the front element.",
#                 "children": []
#               }
#             ]
#           }
#         ]
#       }
#     }
#   ]
#     }"""
    run_speech_model(client, input_text)
    
    # img = extract_image_from_pdf("./test_input/LinearRegression.pdf", 17, (150, 150, 800, 250))
    # base64_image = encode_image(img)

    # Testing with an image
    # img_path = "./test_input/image3.png"
    # with Image.open(img_path) as img:
    #     base64_image = encode_image(img)
    
    # arr = run_model(client, "Please explain the following concepts", base64_image)
    # print(arr)