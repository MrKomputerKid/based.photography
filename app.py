import flask
from flask import Flask, render_template, jsonify, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import os
import magic
from upload import allowed_file

app = Flask(__name__)

# Set the maximum upload size to 16 megabytes
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize magic library for MIME types.
mime = magic.Magic

def is_valid_file(file):
    # Check if the file has an allowed extension
    if allowed_file(file.filename)
        # Check if the files content type is an image
        content_type = mime.from_buffer(file.read(1024)) # Read the first 1024 bytes for content type detection.
        return content_type.startswith('image/')
    return False


@app.route('/')
def index():
    # Get the list of files in the UPLOAD_FOLDER directory
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    # Sort the files by modification time in descending order
    files.sort(key=lambda x: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], x)), reverse=True)
    # Select the latest 5 files
    latest_files = files[:5]
    # Render the template with the latest files
    return render_template('index.html', latest_files=latest_files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in flask.request.files:
        return jsonify({'error': 'No file part'}), 400

    file = flask.request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(upload_path):
            return jsonify({'error': 'File already exists!'})
        else:
            file.save(upload_path)
            return redirect(url_for('index'))

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/search', methods=['GET'])
def search_image():
    search_query = flask.request.args.get('name')

    if search_query:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if search_query.lower() == filename.lower():
                return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

        matching_images = [filename for filename in os.listdir(app.config['UPLOAD_FOLDER']) if search_query.lower() in filename.lower()]
        if matching_images:
            return jsonify({'results': matching_images})

    flask.abort(404)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
