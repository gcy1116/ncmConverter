from flask import Flask, render_template, request, jsonify, send_from_directory
from ncmConverter import dump
import os


app = Flask(__name__, static_folder='./static')

@app.route('/')
def home():
    return render_template('index.html')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
converted_folder = os.path.join(UPLOAD_FOLDER, 'converted')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(converted_folder):
    os.makedirs(converted_folder)

@app.route('/convert', methods=['POST'])
def convert_files():
    # 接收文件
    files = request.files.getlist('files')
    for file in files:
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(temp_path)
        
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'converted')
        try:
            dump(temp_path, output_dir)
            print(f'File {file.filename} converted successfully.')
        
        except Exception as e:
            print(f'Error converting file {file.filename}: {e}')
            return jsonify({'error': f'Error converting file {file.filename}: {e}'}), 500
        
        finally:
            os.remove(temp_path)
            print(f'File {file.filename} removed from temporary directory.')

    processed_files = os.listdir(output_dir)
    if processed_files:
        processed_file_path = processed_files[0]
        return jsonify({'downloadUrl': f'/download/{processed_file_path}'})
    else:
        return jsonify({'error': 'No file was processed.'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(converted_folder, filename, as_attachment=True)
