import flask
from flask import Flask, render_template, jsonify, send_from_directory, redirect, url_for
from flask_oauthlib.client import OAuth
from werkzeug.utils import secure_filename
from functools import wraps
from io import StringIO
from getpass import getuser
import os
import jwt

app = Flask(__name__)

secret_key = os.environ.get('YOUR_SECRET_KEY')

oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key='YOUR_GOOGLE_CLIENT_ID',
    consumer_secret='YOUR_SECRET',
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

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
