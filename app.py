import io
import json
from functools import wraps

import click
import numpy as np
import scipy.spatial.distance
import tensorflow as tf
from dotenv import load_dotenv
from flask import (Flask, flash, g, jsonify, redirect, render_template,
                   request, session, url_for)
from PIL import Image
from sqlalchemy import exists, select
from werkzeug.exceptions import NotFound

from db import database
from facial_detection import (extract_face,
                              preprocess_image_into_3channel_array, vggface)
from model import User

load_dotenv()

app = Flask(__name__)
app.config.from_prefixed_env()
database.init_app(app)


def get_user(name):
    session = database.get_session()
    if not session.query(exists().where(User.username == name)).scalar():
        raise NotFound
    stmt = select(User).where(User.username == name)
    return session.scalar(stmt)


def extract_features(img_stream):
    image = Image.open(io.BytesIO(img_stream))
    face_array = extract_face(image, preprocess_image_into_3channel_array)
    face_array = tf.image.resize(face_array, (224, 224))
    face_array = face_array[np.newaxis, :, :, :]
    feature_array = vggface(face_array)
    feature_array = tf.reshape(feature_array, (-1, ))
    return feature_array


def create_user(name, facial_features):
    session = database.get_session()
    user = User(name, vector=facial_features)
    session.add(user)
    session.flush()


def validate_data(request):
    name = request.form.get('username')
    photo = request.files.get('photo')
    image_stream = photo.stream.read()

    if name and image_stream:
        return True, (name, image_stream)
    return False, (None, None)


def validate_login_submission(user_credentials, login_credentials):
    similarity = scipy.spatial.distance.cosine(
        user_credentials, login_credentials)
    return 1 - similarity > 0.7


def login(user):
    session['username'] = user.username


def logout():
    session.pop('username')


def protected(f):
    @wraps(f)
    def _(*args, **kwargs):
        if 'username' not in session:
            flash('Unauthorized access! Please login first.')
            return redirect(url_for('main'))
        return f(*args, **kwargs)
    return _


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/register-user')
def show_user_registration_form():
    return render_template('registration.html')


@app.post('/register-user')
def register_user():
    validated, (name, image_stream) = validate_data(request)
    if validated:
        feature_array = extract_features(image_stream)
        create_user(name, feature_array)
        flash(f"{name} successfully registered.")
        return json.dumps({'status': "201", "redirect": url_for('main')})
    return json.dumps({'status': "400"})


@app.route('/login', methods=['get', 'post'])
def login_user():
    if request.method == 'POST':
        validated, (name, image_stream) = validate_data(request)
        if validated:
            # flash('I received a photo')
            user = get_user(name)
            user_features = tf.io.decode_raw(user.face, tf.float32)
            login_features = extract_features(image_stream)
            is_a_valid_login = validate_login_submission(
                user_features, login_features)
            if is_a_valid_login:
                flash(f'Login successful! Welcome, {name}')
                login(user)
                return jsonify({
                    'status': '200',
                    'redirect': url_for('main'),
                })
            flash(
                f'Login unsuccessful')
            return jsonify({
                'status': '403',
                'redirect': url_for('login_user')
            })
        flash(f'Login unsuccessful. No image received.')
        return redirect(url_for('main'))
    return render_template('login.html')


@app.route('/protected')
@protected
def protected_resource():
    user = get_user(session['username'])
    return render_template('protected.html', user=user)


@app.route('/logout')
@protected
def logout_user():
    logout()
    flash('Successfully logged out! Please come again!')
    return redirect(url_for('main'))


@app.errorhandler(NotFound)
def handle_user_not_found(e):
    flash('User not found')
    return redirect(url_for('login_user'))


@app.cli.command("create-user")
@click.option('-n', '--name', help='User name')
@click.option('-i', '--image-file', help='Path to image file')
def create_user_command(name, image_file):
    stream = open(image_file, 'rb').read()
    image_features = extract_features(stream)
    create_user(name, image_features)


@app.cli.command("list-users")
def list_user_command():
    session = database.get_session()
    results = session.scalars(select(User.username)).all()
    for i, name in enumerate(results):
        click.echo(name)
    click.echo(f"Retrieved {i+1} records.")


@app.cli.command("delete-user")
@click.argument("username")
def delete_user_command(username):
    session = database.get_session()
    user = get_user(username)
    session.delete(user)
    click.echo(f"User {user.username} deleted.")


@app.teardown_appcontext
def pop_db_session(e):
    if 'session' in g:
        session = g.pop('session')
        session.commit()
        session.close()
