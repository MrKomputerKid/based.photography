from flask import Flask, request, jsonify, render_template
from flask_httpauth import SSHAuth
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
ssh_auth = SSHAuth()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SSH_AUTH'] = ssh_auth
app.config['SECRET_KEY'] = 'your_ssh_secret_key'  # Replace with a strong secret key

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@ssh_auth.login_required  # Requires valid SSH key for access
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'success': True, 'message': 'File uploaded successfully'}), 200

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/search', methods=['GET'])
def search_image():
    image_url = request.args.get('url')
    # Add your image search logic here based on the provided URL
    return jsonify({'url': image_url})

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
