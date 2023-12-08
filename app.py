import flask
from flask import Flask
from flask_basicauth import BasicAuth
from werkzeug.utils import secure_filename
from paramiko import RSAKey, SSHException
from functools import wraps
from io import StringIO
from getpass import getuser
import os
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
basic_auth = BasicAuth(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Set basic authentication creds
app.config['BASIC_AUTH_USERNAME'] = getuser()
app.config['BASIC_AUTH_PASSWORD'] = 'UR_PASS'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Time interval for re-authentication (15 minutes in this example)
REAUTH_INTERVAL = timedelta(minutes=15)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_reauthentication(func):
    last_auth_time = datetime.utcnow()

    def wrapper(*args, **kwargs):
        nonlocal last_auth_time

        # Check if it's time to re-authenticate
        if datetime.utcnow() - last_auth_time > REAUTH_INTERVAL:
            return basic_auth.unauthorized()

        response = func(*args, **kwargs)

        # Update the last authentication time
        last_auth_time = datetime.utcnow()

        return response

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
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(upload_path):
            return flask.jsonify({'error': 'File already exists!'})
        else:
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
