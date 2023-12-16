import os
import logging
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import requests

# Configure Logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Basic Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_PATH'] = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB upload limit
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# Ensure upload directory exists
os.makedirs(app.config['MAX_CONTENT_PATH'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
api_key = os.environ.get('GEMINI_KEY')

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
    try:
        if request.method == 'POST':
            file = request.files['file']
            question_prompt = request.form['question']

            if file and allowed_file(file.filename) and question_prompt:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['MAX_CONTENT_PATH'], filename)
                file.save(file_path)

                response_text = generate_gemini_response(file_path, question_prompt)
                return render_template('index.html', response=response_text)

        return render_template('index.html')
    except Exception as e:
        app.logger.error(f'Error: {e}')
        return render_template('index.html', error="An error occurred")

def generate_gemini_response(image_loc, question_prompt):
    with open(image_loc, 'rb') as image_file:
        image_data = {
            "mime_type": "image/jpeg",
            "data": image_file.read()
        }

    prompt_parts = [input_prompt, image_data, {"text": question_prompt}]
    response = model_generate_content(prompt_parts)
    return response.text if response else "Error in response"

def model_generate_content(prompt_parts):
    api_endpoint = "YOUR_GEMINI_API_ENDPOINT"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(api_endpoint, json={"prompt": prompt_parts}, headers=headers)
        return response.json()
    except requests.RequestException as e:
        app.logger.error(f'API Request Error: {e}')
        return None

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run()
