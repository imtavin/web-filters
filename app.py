import os
import uuid
import json
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from flask_cors import CORS

# Configurações da aplicação
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

CORS(app)

# Garante que os diretórios existam
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply', methods=['POST'])
def apply_filters():
    # Verifica se o arquivo foi enviado
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    # Verifica se o arquivo tem nome
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    # Verifica a extensão do arquivo
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
    
    # Salva o arquivo
    filename = secure_filename(file.filename)
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(img_path)
    
    # Processa os filtros
    filters = json.loads(request.form.get('filters', '[]'))
    result_filename = f"{uuid.uuid4().hex}.png"
    result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
    
    # Aplica os filtros
    img = cv2.imread(img_path)
    if img is None:
        return jsonify({'error': 'Não foi possível ler a imagem'}), 400
    
    for f in filters:
        img = apply_filter(img, f)
    
    # Salva o resultado
    success = cv2.imwrite(result_path, img)
    if not success:
        return jsonify({'error': 'Falha ao salvar imagem processada'}), 500
    
    # Obtém as dimensões da imagem resultante
    height, width = img.shape[:2]
    
    return jsonify({
        'image_url': f'/static/results/{result_filename}',
        'dimensions': f"{width}×{height}"
    })

def apply_filter(img, filter_config):
    """Aplica um único filtro na imagem"""
    name = filter_config.get("name")
    params = filter_config.get("params", {})
    
    try:
        # Filtros de conversão de cor
        if name == "gray":
            if len(img.shape) == 3:  # Se for colorida
                return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return img
            
        elif name == "hsv":
            return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
        elif name == "lab":
            return cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            
        # Filtros de suavização
        elif name == "blur":
            ksize = int(params.get("ksize", 5))
            return cv2.GaussianBlur(img, (ksize, ksize), 0)
            
        elif name == "median_blur":
            ksize = int(params.get("ksize", 5))
            return cv2.medianBlur(img, ksize)
            
        elif name == "bilateral":
            d = int(params.get("d", 9))
            sigma_color = int(params.get("sigma_color", 75))
            sigma_space = int(params.get("sigma_space", 75))
            return cv2.bilateralFilter(img, d, sigma_color, sigma_space)
            
        # Filtros morfológicos
        elif name == "erode":
            ksize = int(params.get("ksize", 3))
            iterations = int(params.get("iterations", 1))
            kernel = np.ones((ksize, ksize), np.uint8)
            return cv2.erode(img, kernel, iterations=iterations)
            
        elif name == "dilate":
            ksize = int(params.get("ksize", 3))
            iterations = int(params.get("iterations", 1))
            kernel = np.ones((ksize, ksize), np.uint8)
            return cv2.dilate(img, kernel, iterations=iterations)
            
        elif name == "opening":
            ksize = int(params.get("ksize", 3))
            kernel = np.ones((ksize, ksize), np.uint8)
            return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
            
        elif name == "closing":
            ksize = int(params.get("ksize", 3))
            kernel = np.ones((ksize, ksize), np.uint8)
            return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
            
        # Filtros de borda
        elif name == "canny":
            threshold1 = int(params.get("threshold1", 100))
            threshold2 = int(params.get("threshold2", 200))
            return cv2.Canny(img, threshold1, threshold2)
            
        elif name == "sobel":
            dx = int(params.get("dx", 1))
            dy = int(params.get("dy", 1))
            ksize = int(params.get("ksize", 3))
            return cv2.Sobel(img, cv2.CV_64F, dx, dy, ksize=ksize)
            
        elif name == "laplacian":
            ksize = int(params.get("ksize", 3))
            return cv2.Laplacian(img, cv2.CV_64F, ksize=ksize)
            
        # Transformações
        elif name == "rotate":
            angle = int(params.get("angle", 90))
            h, w = img.shape[:2]
            M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
            return cv2.warpAffine(img, M, (w, h))
            
        elif name == "flip":
            flip_code = int(params.get("code", 1))  # 0: vertical, 1: horizontal, -1: ambos
            return cv2.flip(img, flip_code)
            
        # Operações de cor
        elif name == "invert":
            return cv2.bitwise_not(img)
            
        elif name == "threshold":
            thresh = int(params.get("thresh", 127))
            maxval = int(params.get("maxval", 255))
            type_ = params.get("type", "binary")
            
            if type_ == "binary":
                _, result = cv2.threshold(img, thresh, maxval, cv2.THRESH_BINARY)
            elif type_ == "binary_inv":
                _, result = cv2.threshold(img, thresh, maxval, cv2.THRESH_BINARY_INV)
            elif type_ == "trunc":
                _, result = cv2.threshold(img, thresh, maxval, cv2.THRESH_TRUNC)
            elif type_ == "tozero":
                _, result = cv2.threshold(img, thresh, maxval, cv2.THRESH_TOZERO)
            elif type_ == "tozero_inv":
                _, result = cv2.threshold(img, thresh, maxval, cv2.THRESH_TOZERO_INV)
            elif type_ == "otsu":
                _, result = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            else:
                _, result = cv2.threshold(img, thresh, maxval, cv2.THRESH_BINARY)
            return result
            
        elif name == "adaptive_threshold":
            maxval = int(params.get("maxval", 255))
            method = params.get("method", "gaussian")
            type_ = params.get("type", "binary")
            block_size = int(params.get("block_size", 11))
            C = int(params.get("C", 2))
            
            if method == "mean":
                method = cv2.ADAPTIVE_THRESH_MEAN_C
            else:
                method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
                
            if type_ == "binary":
                type_ = cv2.THRESH_BINARY
            else:
                type_ = cv2.THRESH_BINARY_INV
                
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
            return cv2.adaptiveThreshold(img, maxval, method, type_, block_size, C)
            
        # Efeitos especiais
        elif name == "sketch":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            inv_gray = 255 - gray
            blurred = cv2.GaussianBlur(inv_gray, (21, 21), 0)
            inv_blurred = 255 - blurred
            return cv2.divide(gray, inv_blurred, scale=256.0)
            
        elif name == "sepia":
            kernel = np.array([[0.272, 0.534, 0.131],
                              [0.349, 0.686, 0.168],
                              [0.393, 0.769, 0.189]])
            return cv2.transform(img, kernel)
            
        elif name == "pencil_sketch":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            inverted = 255 - gray
            blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
            inverted_blurred = 255 - blurred
            sketch = cv2.divide(gray, inverted_blurred, scale=256.0)
            return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
            
        # Filtros avançados
        elif name == "histogram_equalization":
            if len(img.shape) == 2:  # Grayscale
                return cv2.equalizeHist(img)
            else:  # Color
                ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
                ycrcb[:,:,0] = cv2.equalizeHist(ycrcb[:,:,0])
                return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
                
        elif name == "clahe":
            clip_limit = float(params.get("clip_limit", 2.0))
            grid_size = int(params.get("grid_size", 8))
            
            if len(img.shape) == 2:  # Grayscale
                clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(grid_size, grid_size))
                return clahe.apply(img)
            else:  # Color
                lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(grid_size, grid_size))
                l = clahe.apply(l)
                lab = cv2.merge((l, a, b))
                return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
                
        return img
        
    except Exception as e:
        print(f"Erro ao aplicar filtro {name}: {str(e)}")
        return img

@app.route('/export', methods=['POST'])
def export_code():
    """Gera e retorna o código Python com os filtros aplicados"""
    filters_data = request.json.get("filters", [])
    code = generate_python_code(filters_data)
    return jsonify({"code": code})

def generate_python_code(filters):
    """Gera o código Python equivalente aos filtros aplicados"""
    code_lines = [
        "import cv2",
        "import numpy as np",
        "",
        "# Carregar imagem",
        "img = cv2.imread('input.jpg')  # Substitua pelo caminho da sua imagem",
        ""
    ]
    
    for f in filters:
        name = f.get("name")
        params = f.get("params", {})
        
        if name == "gray":
            code_lines.append("# Converter para escala de cinza")
            code_lines.append("img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)")
            
        elif name == "blur":
            ksize = params.get("ksize", 5)
            code_lines.append(f"# Aplicar desfoque gaussiano (kernel {ksize}x{ksize})")
            code_lines.append(f"img = cv2.GaussianBlur(img, ({ksize}, {ksize}), 0)")
            
        elif name == "median_blur":
            ksize = params.get("ksize", 5)
            code_lines.append(f"# Aplicar desfoque mediano (kernel {ksize}x{ksize})")
            code_lines.append(f"img = cv2.medianBlur(img, {ksize})")
            
        elif name == "bilateral":
            d = params.get("d", 9)
            sigma_color = params.get("sigma_color", 75)
            sigma_space = params.get("sigma_space", 75)
            code_lines.append("# Aplicar filtro bilateral")
            code_lines.append(f"img = cv2.bilateralFilter(img, {d}, {sigma_color}, {sigma_space})")
            
        elif name == "threshold":
            thresh = params.get("thresh", 127)
            maxval = params.get("maxval", 255)
            type_ = params.get("type", "binary")
            code_lines.append("# Aplicar threshold")
            
            if type_ == "binary":
                code_lines.append(f"_, img = cv2.threshold(img, {thresh}, {maxval}, cv2.THRESH_BINARY)")
            elif type_ == "binary_inv":
                code_lines.append(f"_, img = cv2.threshold(img, {thresh}, {maxval}, cv2.THRESH_BINARY_INV)")
            elif type_ == "trunc":
                code_lines.append(f"_, img = cv2.threshold(img, {thresh}, {maxval}, cv2.THRESH_TRUNC)")
            elif type_ == "tozero":
                code_lines.append(f"_, img = cv2.threshold(img, {thresh}, {maxval}, cv2.THRESH_TOZERO)")
            elif type_ == "tozero_inv":
                code_lines.append(f"_, img = cv2.threshold(img, {thresh}, {maxval}, cv2.THRESH_TOZERO_INV)")
            elif type_ == "otsu":
                code_lines.append(f"_, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)")
                
        # Adicione condições para todos os outros filtros...
        else:
            code_lines.append(f"# Filtro {name} - Parâmetros: {json.dumps(params)}")
            code_lines.append("# Implementação não gerada automaticamente")
        
        code_lines.append("")
    
    code_lines.append("# Salvar resultado")
    code_lines.append('cv2.imwrite("output.png", img)')
    code_lines.append("")
    code_lines.append("# Mostrar imagem (opcional)")
    code_lines.append('cv2.imshow("Resultado", img)')
    code_lines.append('cv2.waitKey(0)')
    code_lines.append('cv2.destroyAllWindows()')
    
    return '\n'.join(code_lines)

@app.route('/static/results/<filename>')
def serve_result(filename):
    """Serve as imagens processadas"""
    return send_from_directory(app.config['RESULT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)