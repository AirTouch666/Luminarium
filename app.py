import sys
import os
import json
import secrets
import hashlib
from flask import Flask, request, render_template, send_from_directory, url_for, redirect, session, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import io

app = Flask(__name__)

base_path = os.path.abspath(os.path.dirname(__file__))

CONFIG_FILE = os.path.join(base_path, 'config.json')
UPLOAD_FOLDER = os.path.join(base_path, 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_languages():
    with open(os.path.join(base_path, 'languages.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

def load_or_create_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        config = {
            'secret_key': secrets.token_hex(16),
            'port': 8080,
            'background': '#f4f4f4',
            'site_name': 'Luminarium',
            'site_icon': '',
            'max_file_size': 10,
            'allowed_extensions': ["png", "jpg", "jpeg", "gif", "webp"],
            'convert_to_webp': ["png", "jpg", "jpeg"],
            'domain': '',
            'language': 'zh'
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return config

config = load_or_create_config()
app.secret_key = config['secret_key']
PORT = config.get('port', 8080)
BACKGROUND = config.get('background', '#f4f4f4')
SITE_NAME = config.get('site_name', 'Luminarium')
SITE_ICON = config.get('site_icon', '')
MAX_FILE_SIZE = config.get('max_file_size', 10) * 1024 * 1024  
ALLOWED_EXTENSIONS = set(config.get('allowed_extensions', ["png", "jpg", "jpeg", "gif", "webp"]))
CONVERT_TO_WEBP = set(config.get('convert_to_webp', ["png", "jpg", "jpeg"]))
DOMAIN = config.get('domain', '')
LANGUAGES = load_languages()
CURRENT_LANG = config.get('language', 'zh')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_webp(image):
    webp_io = io.BytesIO()
    image.save(webp_io, 'WEBP', quality=85)
    webp_io.seek(0)
    return webp_io

def get_file_hash(file_content):
    return hashlib.md5(file_content).hexdigest()

def get_unique_filename(file_content, original_filename):
    file_hash = get_file_hash(file_content)
    _, ext = os.path.splitext(original_filename)
    return f"{file_hash}{ext}"

def get_file_url(filename):
    if DOMAIN:
        if DOMAIN.startswith(('http://', 'https://')):
            return f"{DOMAIN.rstrip('/')}/{filename}"
        else:
            return f"https://{DOMAIN.rstrip('/')}/{filename}"
    else:
        return url_for('uploaded_file', filename=filename, _external=True)

def get_uploaded_files():
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.lower().split('.')[-1] in ALLOWED_EXTENSIONS:
            file_url = get_file_url(filename)  
            files.append({'name': filename, 'url': file_url})
    return sorted(files, key=lambda x: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], x['name'])), reverse=True)

def get_background():
    bg = BACKGROUND
    if bg.startswith(('http://', 'https://')):
        return {'type': 'url', 'value': bg}
    elif os.path.isfile(bg):
        if DOMAIN:
            filename = os.path.basename(bg)
            if DOMAIN.startswith(('http://', 'https://')):
                bg_url = f"{DOMAIN.rstrip('/')}/custom_background/{filename}"
            else:
                bg_url = f"https://{DOMAIN.rstrip('/')}/custom_background/{filename}"
            return {'type': 'file', 'value': bg_url}
        else:
            return {'type': 'file', 'value': url_for('custom_background', filename=os.path.basename(bg))}
    else:
        return {'type': 'color', 'value': bg}

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            error_msg = '没有选择文件'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': error_msg}), 400
            return redirect(url_for('upload_file', error=error_msg))
        
        files = request.files.getlist('file')
        if not files or files[0].filename == '':
            error_msg = '没有选择任何文件'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': error_msg}), 400
            return redirect(url_for('upload_file', error=error_msg))
        
        uploaded_files = []
        errors = []
        for file in files:
            if file and allowed_file(file.filename):
                try:
                    file_content = file.read()
                    if len(file_content) > MAX_FILE_SIZE:
                        raise ValueError(f"文件 {file.filename} 超过大小限制 ({MAX_FILE_SIZE/1024/1024:.1f}MB)")
                    
                    try:
                        image = Image.open(io.BytesIO(file_content))
                    except Exception as e:
                        raise ValueError(f"文件 {file.filename} 不是有效的图片文件")

                    filename = get_unique_filename(file_content, file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
                    file_ext = filename.rsplit('.', 1)[1].lower()
                    if file_ext in CONVERT_TO_WEBP:
                        try:
                            webp_io = convert_to_webp(image)
                            webp_filename = os.path.splitext(filename)[0] + '.webp'
                            webp_path = os.path.join(app.config['UPLOAD_FOLDER'], webp_filename)
                            with open(webp_path, 'wb') as f:
                                f.write(webp_io.getvalue())
                            filename = webp_filename
                        except Exception as e:
                            raise ValueError(f"转换文件 {file.filename} 为WebP格式失败: {str(e)}")
                    else:
                        with open(file_path, 'wb') as f:
                            f.write(file_content)
                    
                    file_url = get_file_url(filename)
                    uploaded_files.append(file_url)
                except Exception as e:
                    app.logger.error(f"处理文件失败: {str(e)}")
                    errors.append(str(e))
            else:
                errors.append(f"文件 {file.filename} 类型不支持，仅支持: {', '.join(ALLOWED_EXTENSIONS)}")
        
        if errors:
            error_msg = '上传过程中出现错误：\n' + '\n'.join(errors)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': error_msg}), 400
            return redirect(url_for('upload_file', error=error_msg))
        
        if uploaded_files:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'file_urls': uploaded_files})
            session['success'] = True
            session['file_urls'] = uploaded_files
            return redirect(url_for('upload_file'))
        else:
            error_msg = '没有文件被成功上传'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': error_msg}), 400
            return redirect(url_for('upload_file', error=error_msg))

    success = session.pop('success', False)
    file_urls = session.pop('file_urls', [])
    error = request.args.get('error')
    uploaded_files = get_uploaded_files()
    background = get_background()
    return render_template('index.html', 
                         success=success, 
                         file_urls=file_urls, 
                         error=error, 
                         uploaded_files=uploaded_files, 
                         background=background, 
                         site_name=SITE_NAME, 
                         site_icon=SITE_ICON,
                         lang=LANGUAGES[CURRENT_LANG], 
                         current_lang=CURRENT_LANG,    
                         available_langs=list(LANGUAGES.keys()),
                         LANGUAGES=LANGUAGES)

@app.route('/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/custom_background/<filename>')
def custom_background(filename):
    directory = os.path.dirname(BACKGROUND)
    return send_from_directory(directory, filename)

@app.route('/get_settings')
def get_settings():
    return jsonify({
        'site_name': SITE_NAME,
        'site_icon': SITE_ICON,
        'max_file_size': MAX_FILE_SIZE // (1024 * 1024),  
        'allowed_extensions': list(ALLOWED_EXTENSIONS),
        'background': BACKGROUND,
        'convert_to_webp': list(CONVERT_TO_WEBP),
        'domain': DOMAIN  
    })

@app.route('/save_settings', methods=['POST'])
def save_settings():
    global SITE_NAME, SITE_ICON, MAX_FILE_SIZE, ALLOWED_EXTENSIONS, BACKGROUND, CONVERT_TO_WEBP, DOMAIN
    data = request.json
    SITE_NAME = data['site_name']
    SITE_ICON = data['site_icon']
    MAX_FILE_SIZE = int(data['max_file_size']) * 1024 * 1024  
    ALLOWED_EXTENSIONS = set(data['allowed_extensions'])
    BACKGROUND = data['background']
    CONVERT_TO_WEBP = set(data['convert_to_webp'])
    DOMAIN = data['domain']  

    config = load_or_create_config()
    config.update({
        'site_name': SITE_NAME,
        'site_icon': SITE_ICON,
        'max_file_size': int(data['max_file_size']),
        'allowed_extensions': list(ALLOWED_EXTENSIONS),
        'background': BACKGROUND,
        'convert_to_webp': list(CONVERT_TO_WEBP),
        'domain': DOMAIN  
    })
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

    return jsonify({'success': True})

@app.route('/change_language/<lang>', methods=['POST'])
def change_language(lang):
    global CURRENT_LANG
    if lang in LANGUAGES:
        CURRENT_LANG = lang
        config = load_or_create_config()
        config['language'] = lang
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=PORT, debug=False)