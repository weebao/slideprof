import json
import fitz 
import os

def load_json(json_file_path):
    with open(json_file_path, 'r') as json_file:
        return json.load(json_file)

def get_text_width(text, fontsize, fontname="helv"):
    return fitz.get_text_length(text, fontname=fontname, fontsize=fontsize)

def add_summary_page(doc, summary_text):
    summary_page = doc.new_page(width=doc[0].rect.width, height=doc[0].rect.height)
    
    margin = 72  
    text_position = fitz.Point(margin, margin)
    font_size = 18  
    right_margin = doc[0].rect.width - margin
    line_height = 28  
    fontname = "helv"
    
    summary_lines = summary_text.split("\n")
    
    for line in summary_lines:
        if line.strip().startswith("-"):
            line = "• " + line.strip()[1:].strip()
        
        words = line.split()
        current_line = ""
        for word in words:
            if get_text_width(current_line + " " + word, fontsize=font_size, fontname=fontname) < (right_margin - text_position.x):
                current_line += " " + word
            else:
                summary_page.insert_text(text_position, current_line.strip(), fontsize=font_size, fontname=fontname)
                text_position.y += line_height
                current_line = word
        
        if current_line:
            summary_page.insert_text(text_position, current_line.strip(), fontsize=font_size, fontname=fontname)
            text_position.y += line_height
        
        if text_position.y > doc[0].rect.height - margin - line_height:
            summary_page = doc.new_page(width=doc[0].rect.width, height=doc[0].rect.height)
            text_position = fitz.Point(margin, margin)

def merge_pdf_with_summaries(pdf_path, data, output_pdf_path):
    doc = fitz.open(pdf_path)
    
    new_doc = fitz.open()
    
    for page_num in range(len(doc)):
        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
        key = f"page_{page_num + 1}.png"
        if key in data:
            summary = data[key].get("summary", "")
            add_summary_page(new_doc, summary)
    
    new_doc.save(output_pdf_path)
    new_doc.close()
    doc.close()

if __name__ == "__main__":
    json_file_path = './test_output/segmented_transcriptions_with_summaries.json'
    pdf_file_path = './test_input/8.pdf'
    output_pdf_path = './test_output/modified_pdf_file.pdf'
    
    data = load_json(json_file_path)
    
    if pdf_file_path == output_pdf_path:
        base, ext = os.path.splitext(pdf_file_path)
        output_pdf_path = f"{base}_with_summaries{ext}"
    
    merge_pdf_with_summaries(pdf_file_path, data, output_pdf_path)
    print(f"New PDF with summaries saved as: {output_pdf_path}")