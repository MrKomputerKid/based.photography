import flask
from flask import Flask, session, url_for
from werkzeug.utils import secure_filename
from getpass import getuser
import os
import magic

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initalize magic library for MIME type detection
mime = magic.Magic()

def allowed_file(filename):
    # Check if the filename has an allowed extension
    if '.' in filename:
        # Split the filename and extension
        name, extension = filename.rsplit('.', 1)

        # Check if the extension is in the allowed set
        if extension.lower() in ALLOWED_EXTENSIONS:
            # Ensure that there are no additional dots in the name part
            if '.' not in name:
                return True

    return False

def is_valid_file(file):
    # Check if the file's content type is an image
    file.seek(0)  # Move the file cursor to the beginning
    content_type = mime.from_buffer(file.read(1024))  # Read the first 1024 bytes for content type detection
    print("Detected MIME type:", content_type)  # Print the detected MIME type for debugging

    # Check if the detected MIME type contains any of the expected image types as a substring (lenient check)
    expected_image_types = {'image/png', 'image/jpeg', 'image/jpg', 'image/gif'}
    return any(image_type.lower() in content_type.lower() for image_type in expected_image_types)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in flask.request.files:
        return flask.jsonify({'error': 'No file part'}), 400

    file = flask.request.files['file']

    if file.filename == '':
        return flask.jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.exists(upload_path):
            return flask.jsonify({'error': 'File already exists'}), 400

        file.save(upload_path)
        return flask.redirect(url_for('index'))

    return flask.jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
