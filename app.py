import os
import uuid
import json
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from utils import filters 

app = Flask(__name__)

UPLOAD_FOLDER = 'static/upload'
RESULT_FOLDER = 'static/results'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply', methods=['POST'])
def apply():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    filename = secure_filename(file.filename)
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(img_path)

    filter_list = json.loads(request.form.get('filters', '[]'))  # Renomeado para filter_list

    result_filename = f"{uuid.uuid4().hex}.png"
    result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)

    filters.apply_filters(img_path, filter_list, result_path)  # Usando filter_list

    return jsonify({'image_url': f'/static/results/{result_filename}'})

@app.route('/export', methods=['POST'])
def export():
    filters_data = request.json.get("filters", [])
    code = filters.generate_code(filters_data)
    return jsonify({"code": code})

if __name__ == '__main__':
    app.run(debug=True)