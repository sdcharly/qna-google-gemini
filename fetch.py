import google.generativeai as genai
from pathlib import Path
import os
from flask import Flask, request, render_template

# Set up Flask
app = Flask(__name__)

# Configure the Google API
def configure_genai(api_key):
    genai.configure(api_key=AIzaSyDe6-BlLPkv2T1h6igWdyTouBhopx9m1XU)

    generation_config = {
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 4096,
    }

    safety_settings = [
        # Safety settings as per your configuration
    ]

    model = genai.GenerativeModel(model_name="gemini-pro-vision",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)
    return model

# Function to prepare image input
def input_image_setup(file_loc):
    if not Path(file_loc).exists():
        raise FileNotFoundError(f"Could not find image: {file_loc}")

    image_parts = [
        {
            "mime_type": "image/jpeg",
            "data": Path(file_loc).read_bytes()
        }
    ]
    return image_parts

# Function to generate response
def generate_gemini_response(model, input_prompt, image_loc, question_prompt):
    image_prompt = input_image_setup(image_loc)
    prompt_parts = [input_prompt, image_prompt[0], question_prompt]
    response = model.generate_content(prompt_parts)
    return response.text

# Flask route for handling the form submission
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'

        file = request.files['file']
        if file.filename == '':
            return 'No selected file'

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            file.save(file_path)

            # Set up model and generate response
            model = configure_genai(os.environ.get('Gemini_Key'))
            input_prompt = """
                           You are an expert in understanding invoices.
                           You will receive input images as invoices &
                           you will have to answer questions based on the input image
                           """
            question_prompt = "What is the total amount in the invoice?"
            result = generate_gemini_response(model, input_prompt, file_path, question_prompt)
            return result

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
