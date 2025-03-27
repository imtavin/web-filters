import os
from flask import Flask, request, render_template, redirect, send_file
from werkzeug.utils import secure_filename
from utils import filters

UPLOAD_FOLDER = './static/upload'
TEMPLATE_FOLDER = './template'

app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'there is no file in form!'
        file = request.files['file']
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        filter_request = request.form['filter']

        if filter_request == 'gray':
            filter_path = filters.gray(path) 
            return render_template('index.html', filename=filter_path)

        if filter_request == 'blur':
            filter_path = filters.blur(path) 
            return render_template('index.html', filename=filter_path)
        
        if filter_request == 'thresholding':
            filter_path = filters.thresholding(path) 
            return render_template('index.html', filename=filter_path)
        
        if filter_request == 'erode':
            filter_path = filters.erode(path) 
            return render_template('index.html', filename=filter_path)
        
        if filter_request == 'dilate':
            filter_path = filters.dilate(path) 
            return render_template('index.html', filename=filter_path)
        
        if filter_request == 'open':
            filter_path = filters.open(path) 
            return render_template('index.html', filename=filter_path)
        
        if filter_request == 'close':
            filter_path = filters.close(path) 
            return render_template('index.html', filename=filter_path)

    return render_template('index.html')

if __name__ == '__main__':
    app.run()