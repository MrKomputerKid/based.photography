from flask import Flask, request, jsonify, render_template
from paramiko import RSAKey, SSHException
from functools import wraps
from io import StringIO
import os
import jwt

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key
app.config['AUTHORIZED_KEYS_PATH'] = '/path/to/authorized_keys'  # Replace with the path to your authorized_keys file

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def authenticate_ssh_key(username, key):
    authorized_keys_path = app.config['AUTHORIZED_KEYS_PATH']
    authorized_keys = open(authorized_keys_path).read().splitlines()

    try:
        key_obj = RSAKey(file_obj=StringIO(key))
    except SSHException:
        return False

    return key_obj.get_name() in authorized_keys

def generate_temporary_token(username):
    expiration_time = datetime.utcnow() + timedelta(minutes=30)
    payload = {'sub': username, 'exp': expiration_time}
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def require_token_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401

        token = token.split(' ')[1]

        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            username = decoded_token.get('sub')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return func(*args, **kwargs)

    return wrapper

@app.route('/')
def index():
    username = request.args.get('username')
    if username:
        token = generate_temporary_token(username)
        return jsonify({'token': token.decode('utf-8')})
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@require_token_auth  # Requires valid SSH key for access
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