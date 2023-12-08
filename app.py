import flask
from flask_basicauth import BasicAuth
from werkzeug.utils import secure_filename
from paramiko import RSAKey, SSHException
from functools import wraps
from io import StringIO
from getpass import getuser
import os
import jwt
from datetime import datetime, timedelta

app = flask.Flask(__name__, template_folder='/path/to/template/')
basic_auth = BasicAuth(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Set basic authentication creds
app.config['BASIC_AUTH_USERNAME'] = getuser()
app.config['BASIC_AUTH_PASSWORD'] = 'SUPER SECRET PASSWORD HERE'

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
        token = flask.request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return flask.jsonify({'error': 'Unauthorized'}), 401

        token = token.split(' ')[1]

        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            username = decoded_token.get('sub')
        except jwt.ExpiredSignatureError:
            return flask.jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return flask.jsonify({'error': 'Invalid token'}), 401

        return func(*args, **kwargs)

    return wrapper

@app.route('/')
def index():
    username = flask.request.args.get('username')
    if username:
        token = generate_temporary_token(username)
        return flask.jsonify({'token': token.decode('utf-8')})
    return flask.render_template('index.html')

@app.route('/upload', methods=['POST'])
@basic_auth.required
def upload_file():
    if 'file' not in flask.request.files:
        return flask.jsonify({'error': 'No file part'}), 400

    file = flask.request.files['file']

    if file.filename == '':
        return flask.jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return flask.redirect(flask.url_for('index'))

    return flask.jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/search', methods=['GET'])
def search_image():
    search_query = flask.request.args.get('name')

    if search_query:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if search_query.lower() == filename.lower():
                return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename)

        matching_images = [filename for filename in os.listdir(app.config['UPLOAD_FOLDER']) if search_query.lower() in filename.lower()]
        if matching_images:
            return flask.jsonify({'results': matching_images})

    flask.abort(404)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
