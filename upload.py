from flask import Flask, request, jsonify
from flask_basicauth import BasicAuth
from werkzeug.utils import secure_filename
from getpass import getuser
import os

app = Flask(__name__)
basic_auth = BasicAuth(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Set basic authentication creds
app.config['BASIC_AUTH_USERNAME'] = getuser()
app.config['BASIC_AUTH_PASSWORD'] = 'UR_PASS'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
@basic_auth.required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.exists(upload_path):
            return jsonify({'error': 'File already exists'}), 400

        file.save(upload_path)
        return jsonify({'success': True, 'message': 'File uploaded successfully'}), 200

    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
