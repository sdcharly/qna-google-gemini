import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB upload limit

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Assuming an environment variable 'GEMINI_API_KEY' is set in render.com
api_key = os.environ.get('GEMINI_API_KEY')

# Input prompt for understanding invoices
input_prompt = """
               You are an expert in understanding invoices.
               You will receive input images as invoices &
               you will have to answer questions based on the input image
               """

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        question_prompt = request.form['question']

        if file and allowed_file(file.filename) and question_prompt:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            response_text = generate_gemini_response(file_path, question_prompt)
            return render_template('index.html', response=response_text)

    return render_template('index.html')

def generate_gemini_response(image_loc, question_prompt):
    image_data = {
        "mime_type": "image/jpeg",
        "data": open(image_loc, 'rb').read()
    }
    
    prompt_parts = [input_prompt, image_data, {"text": question_prompt}]
    response = model_generate_content(prompt_parts)
    return response.text if response else "Error in response"

def model_generate_content(prompt_parts):
    # Replace with the appropriate API endpoint and parameters
    api_endpoint = "YOUR_GEMINI_API_ENDPOINT"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt_parts,
        # Add generation_config and safety_settings as required
    }
    try:
        response = requests.post(api_endpoint, json=data, headers=headers)
        return response.json()
    except requests.RequestException as e:
        print(e)
        return None

if __name__ == '__main__':
    app.run(debug=True)
