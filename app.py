from flask import Flask, request, jsonify, send_from_directory
import os
from display.epaper import display_image, display_text

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'bmps'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_image():
    """
    Endpoint to upload BMP images
    """
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser submits an empty file
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check if it's a BMP file
    if not file.filename.lower().endswith('.bmp'):
        return jsonify({'error': 'Only BMP files are allowed'}), 400
    
    # Save the file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Display the image on e-paper display
    success = display_image(file_path)

    if success:
        return jsonify({'message': f'File {file.filename} uploaded and displayed successfully'}), 201
    else:
        return jsonify({'message': f'File {file.filename} uploaded but display failed'}), 500

@app.route('/images', methods=['GET'])
def list_images():
    """
    Endpoint to list all uploaded BMP images
    """
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.lower().endswith('.bmp'):
            files.append(filename)
    
    return jsonify({'images': files})

@app.route('/check', methods=['POST'])
def check_image():
    """
    Endpoint to check if a specific image exists
    """
    data = request.json
    
    if not data or 'filename' not in data:
        return jsonify({'error': 'Filename is required'}), 400
    
    filename = data['filename']
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(file_path):
        return jsonify({'exists': True, 'filename': filename})
    
    return jsonify({'exists': False, 'filename': filename})

@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    """
    Endpoint to retrieve a specific image
    """
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/display-text', methods=['POST'])
def show_text():
    """
    Endpoint to display text on the e-paper display
    """
    data = request.json
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Text content is required'}), 400
    
    text = data['text']
    
    # Optional parameters with defaults
    max_width = data.get('max_width', 122)
    max_height = data.get('max_height', 250)
    
    # Display the text on e-paper display
    success = display_text(text, max_width, max_height)
    
    if success:
        return jsonify({'message': 'Text displayed successfully'}), 200
    else:
        return jsonify({'error': 'Failed to display text'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False)