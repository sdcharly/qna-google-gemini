from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import os
from pathlib import Path

app = Flask(__name__)

# Configure API key
api_key = os.environ.get('GEMINI_KEY')
genai.configure(api_key=api_key)

# Set up the model
generation_config = {
  "temperature": 0.4,
  "top_p": 1,
  "top_k": 32,
  "max_output_tokens": 4096,
}

safety_settings = [
  #... (your safety settings here)
]

model = genai.GenerativeModel(model_name="gemini-pro-vision",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

def input_image_setup(file):
    return [
        {
            "mime_type": "image/jpeg",
            "data": file.read()
        }
    ]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image = request.files['image']
        question = request.form['question']
        input_prompt = """
            You are an expert in understanding invoices.
            You will receive input images as invoices &
            you will have to answer questions based on the input image
            """

        image_prompt = input_image_setup(image)
        prompt_parts = [input_prompt, image_prompt[0], question]
        response = model.generate_content(prompt_parts)

        return jsonify({'response': response.text})
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
