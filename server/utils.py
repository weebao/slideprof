import re

def parse_message_fallback(message):
    print("fallback!!")
    message = message.strip().strip("{}")
    parsed_data = {}

    # Parse the type field
    type_match = re.search(r'"type":\s*"([^"]+)"', message)
    if type_match:
        parsed_data["type"] = type_match.group(1)
    
    # Parse the steps field
    steps_data = re.search(r'"steps":\s*\[(.*)\]', message, re.DOTALL)
    if steps_data:
        steps_content = steps_data.group(1).strip()
        steps = []
        
        # Split individual steps
        step_matches = re.findall(r'{(.*?)}', steps_content, re.DOTALL)
        
        for step in step_matches:
            explanation_match = re.search(r'"explanation":\s*"([^"]+)"', step)
            explanation = explanation_match.group(1) if explanation_match else ""
            
            # Parse items
            items_match = re.search(r'"items":\s*\[(.*)\]', step, re.DOTALL)
            items = []
            if items_match:
                items_content = items_match.group(1).strip()
                item_matches = re.findall(r'{(.*?)}', items_content, re.DOTALL)
                
                for item in item_matches:
                    item_data = {}
                    item_name_match = re.search(r'"item":\s*"([^"]+)"', item)
                    coords_match = re.search(r'"coords":\s*\[(.*?)\]', item)
                    
                    if item_name_match:
                        item_data["item"] = item_name_match.group(1)
                    if coords_match:
                        coords = [float(x) for x in coords_match.group(1).split(',')]
                        item_data["coords"] = coords
                    
                    items.append(item_data)
            
            if explanation != "" and items:
              steps.append({
                  "explanation": explanation,
                  "items": items
              })
        
        parsed_data["steps"] = steps

    return parsed_data