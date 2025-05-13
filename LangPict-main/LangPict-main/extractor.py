css = """
.left-align {text-align: left;}
.shrink-button {width: 100px; background-color: #8E44AD; color: white; border: none; padding: 10px;}
"""

import gradio as gr
import pytesseract as pyt
import snipping_tool as snip
from deep_translator import GoogleTranslator
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
import pandas as pd
import collections
import os
import argparse, json, os, re, shutil, subprocess as sp, yaml
import platform
from gui_theme import gradiocustomtheme
import langid
from transformers import MarianMTModel, MarianTokenizer

project_path = os.getcwd()
paltform_name = platform.system()
if platform == 'Windows':
    os.environ['TESSDATA_PREFIX'] = f'{project_path}\\tesseract'
else:
    os.environ['TESSDATA_PREFIX'] = f'{project_path}/tesseract' 


LANGUAGE_MAP = {
    'N/A': ['N/A'],
    'English': ['en', 'eng'],
    'German': ['de', 'deu'],
    'French': ['fr', 'fra'],
    'Spanish': ['es', 'spa'],
    'Italian': ['it', 'ita'],
    'Portuguese': ['pt', 'por'],
    'Russian': ['ru', 'rus'],
    'Japanese': ['ja', 'jpn'],
    'Korean': ['ko', 'kor'],
    'Chinese': ['zh', 'chi_sim', 'chi_tra'],  
    'Vietnamese': ['vi', 'vie'],
    'Thai': ['th', 'tha'],
    'Arabic': ['ar', 'ara'],
    'Hebrew': ['he', 'heb'],
    'Indonesian': ['id', 'ind'],
    'Turkish': ['tr', 'tur'],
    'Polish': ['pl', 'pol'],
    'Dutch': ['nl', 'nld'],
    'Swedish': ['sv', 'swe'],
    'Danish': ['da', 'dan'],
    'Finnish': ['fi', 'fin'],
    'Norwegian': ['no', 'nor'],
    'Hungarian': ['hu', 'hun'],
    'Czech': ['cs', 'ces'],
    'Slovak': ['sk', 'slk'],
    'Greek': ['el', 'ell'],
    'Latvian': ['lv', 'lav'],
    'Lithuanian': ['lt', 'lit'],
    'Estonian': ['et', 'est'],
    'Ukrainian': ['uk', 'ukr'],
    'Belarusian': ['be', 'bel'],
    'Burmese': ['my', 'mya'],
    'Malay': ['ms', 'mal'],
    'Telugu': ['te', 'tel'],
    'Kannada': ['kn', 'kan'],
    'Tamil': ['ta', 'tam'],
    'Nepali': ['ne', 'nep'],
    'Sinhalese': ['si', 'sin'],
    'Khmer': ['km', 'khm'],
    'Japanese (Vertical)': ['ja', 'jpn_vert'],
}


string_music = ''
current_lang = ''

snip_photo = ""
output_file = f'test'

def ocr_with_language_detection(gr_image):
    global current_lang

    lang = 'eng+ara+deu+fra+ita+spa+rus+zho+por+jpn+kor+ben+hin+tur+vie+tam+tel+mar+kan+urd+pol+srp+ces+kat+ukr+tha+ell+alb+lat+nep+bul+slk+lav+eus+est+srn+hrv+slv+ron+hin+ukr+dan+fin+ind+lav+bul+kan+ara+pan+guj+guj+tet+urd+bho+mlt+som+eus+hrv+gle+kat+som+cor+uzb'

    try:
        print("TESSDATA_PREFIX:", os.environ.get('TESSDATA_PREFIX'))
        sp.run(f'tesseract {gr_image} {output_file} -l {lang}', shell=True, capture_output=True, text=True)
        os.remove(gr_image)
        #text = pd.read_csv(f'{output_file}.txt')
        with open(f"{output_file}.txt", "r", encoding="utf-8") as f:
            text_string = f.read()
        #os.remove(f'{output_file}.txt')
        #text_string = text.to_csv(index=False)
        words_found = text_string.strip()
        current_lang = langid.classify(words_found)[0]
        print(words_found)
    except Exception as e:
        print(e)
        words_found = "Unable to extract the text. Try again."
    return words_found  

def process_image(image):
    if image is None:
        return None, "No image uploaded."
    image = Image.open(image)
    current_image = ImageOps.grayscale(image)
    enhancer = ImageEnhance.Contrast(current_image)
    current_image = enhancer.enhance(2)
    current_image.save("enhanced_temp.png")
    words_found = ocr_with_language_detection("enhanced_temp.png")
    return current_image, words_found


def invoke_snip():
    global snip_photo
    snip_photo = snip.main()  # Call the snipping tool and get the file path
    return snip_photo  # Return the path to the captured image

def radio_choice(request, text_found, Song, Artist): # now that you have the format make a text box for both artist and choice
    new_string = ''
    if request == "Song":
        if Song == "" or text_found not in Song:
            new_string = text_found
        else:
            new_string = Song
        # Update the Song textbox with the value from text_found
        return new_string, Artist  # Return text_found to Song and None for Artist
    elif request == "Artist":
        if Artist == "" or text_found not in Artist:
            new_string = text_found
        else:
            new_string = Artist
        print("hi2")  # This prints when 'Artist' is selected
        # Update the Artist textbox with the value from text_found
        return Song, new_string  # Return text_found to Artist and None for Song
    
    return Song, Artist

def translate_marian(text, tgt_lang):
    global current_lang
    global LANGUAGE_MAP
    two_code = LANGUAGE_MAP[tgt_lang][0]
    print(two_code)
    print(current_lang)
    model_name = f"Helsinki-NLP/opus-mt-{current_lang}-{two_code}"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)

    tokens = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    translated_tokens = model.generate(**tokens)
    translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
    translated_text = translated_text.replace(",", "")
    return translated_text
    
# Create the Gradio interface
gradiocustomtheme_obj = gradiocustomtheme()
with gr.Blocks(theme=gradiocustomtheme_obj, css=css) as demo:#'footer{display:none !important}') as demo:
    gr.Markdown("## Tuning Pic")

    # Image upload component
    if paltform_name == 'Windows':
        snip_button = gr.Button("Snip", elem_classes="left-align shrink-button")
        image_input = gr.Image(type="filepath", label="Upload Picture")
    else:
        image_input = gr.Image(type="filepath", label="Upload Picture")

    # Output components for displaying the processed image and found text
    image_output = gr.Image(label="Enhanced Picture", type="filepath")
    
    text_found = gr.Textbox(label="Extracted Text:", lines=5, interactive=False)

    lang_dropdown = gr.Dropdown(
        choices=list(LANGUAGE_MAP.keys()),  
        label="Choose a Language"
    )
    translate_button = gr.Button("Translate?", elem_classes="left-align shrink-button")

    request = gr.Radio(["Song", "Artist"], label="Select an option then press push")
    choice_button = gr.Button("Push", elem_classes="left-align shrink-button")
    # Translation section
    #dropdown_lang_out = gr.Dropdown(choices=LANGUAGE_MAP.keys(), label="Output Language", value=LANGUAGE_MAP['N/A'][0], interactive=True)
    
    Translation = gr.Textbox(label="Translation:", lines=5, interactive=False)
    Song = gr.Textbox(label="Song:", lines=5, interactive=False)
    Artist = gr.Textbox(label="Artist:", lines=5, interactive=False)
    

    # Update outputs when the image or language changes
    if paltform_name == 'Windows':
        choice_button.click(fn=radio_choice,inputs=[request, text_found, Song, Artist], outputs=[Song, Artist])
        snip_button.click(invoke_snip, outputs=image_input)
        image_input.change(fn=process_image, inputs=image_input, outputs=[image_output, text_found])
        if lang_dropdown != 'N/A':
            translate_button.click(fn = translate_marian, inputs=[text_found,lang_dropdown], outputs=Translation)
    else:
        choice_button.click(fn=radio_choice,inputs=[request, text_found, Song, Artist], outputs=[Song, Artist])
        image_input.change(fn=process_image, inputs=image_input, outputs=[image_output, text_found])
        if lang_dropdown != 'N/A':
            translate_button.click(fn = translate_marian, inputs=[text_found,lang_dropdown], outputs=Translation)


# Launch the Gradio app
demo.launch()

