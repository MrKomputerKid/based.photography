from flask import Flask, request, jsonify, render_template
from paramiko import RSAKey, SSHException, Transport
import os

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

def require_ssh_key_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401

        token = auth_header.split(' ')[1]

        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            username = decoded_token.get('sub')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        key = request.headers.get('SSH-Key')
        if not key or not authenticate_ssh_key(username, key):
            return jsonify({'error': 'Invalid SSH key'}), 401

        return func(*args, **kwargs)

    return wrapper

@app.route('/')
@require_ssh_key_auth
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@require_ssh_key_auth
def upload_file():
    # ... your existing upload logic ...

@app.route('/search', methods=['GET'])
def search_image():
    # ... your existing search logic ...

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
