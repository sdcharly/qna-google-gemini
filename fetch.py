import os
from flask import Flask, request, render_template
from pathlib import Path
import requests

# Assuming an environment variable 'GEMINI_API_KEY' is set in render.com
api_key = os.environ.get('GEMINI_KEY')

app = Flask(fetch)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        question_prompt = request.form.get('question')

        if file and question_prompt:
            file_path = save_file(file)
            response_text = generate_gemini_response(file_path, question_prompt)
            return render_template('index.html', response=response_text)

    return render_template('index.html')

def save_file(file):
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)
    return file_path

def generate_gemini_response(image_loc, question_prompt):
    image_prompt = input_image_setup(image_loc)

    prompt_parts = [image_prompt, question_prompt]
    response = model.generate_content(prompt_parts)
    return response.text

def input_image_setup(file_loc):
    if not (img := Path(file_loc)).exists():
        raise FileNotFoundError(f"Could not find image: {img}")

    image_parts = {
        "mime_type": "image/jpeg",
        "data": Path(file_loc).read_bytes()
    }
    return image_parts

def model_generate_content(prompt_parts):
    # Replace with appropriate API endpoint and parameters
    api_endpoint = "https://example.com/gemini-api"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt_parts,
        "generation_config": generation_config,
        "safety_settings": safety_settings
    }
    response = requests.post(api_endpoint, json=data, headers=headers)
    return response.json()

if __name__ == 'fetch':
    app.run(debug=True)
