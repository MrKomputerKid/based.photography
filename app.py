import flask
from flask import Flask, render_template, jsonify, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import os
import magic
from upload import upload_file, allowed_file, is_valid_file

app = Flask(__name__)

# Set the maximum upload size to 20 megabytes
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
def upload():
    return upload_file()

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
