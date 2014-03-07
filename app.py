from datetime import datetime, timedelta
from hashlib import sha256
import hmac
import json
import os

from flask import abort, Flask, redirect, render_template, request, session, url_for
from dropbox.client import DropboxClient, DropboxOAuth2Flow
from markdown import markdown
import redis
 
redis_url = os.environ['REDISTOGO_URL']
redis_client = redis.from_url(redis_url)
 
# App key and secret from the App console (dropbox.com/developers/apps)
APP_KEY = os.environ['APP_KEY']
APP_SECRET = os.environ['APP_SECRET']
 
app = Flask(__name__)
app.debug = True
 
# A random secret used by Flask to encrypt session data cookies
app.secret_key = os.environ['FLASK_SECRET_KEY']
 
def get_callback_url():
    '''Generate a proper callback URL, forcing HTTPS if not running locally'''
    url = url_for(
        'oauth_callback',
        _external=True,
        _scheme='http' if request.host.startswith('127.0.0.1') else 'https'
    )
    return url
 
def get_flow():
    return DropboxOAuth2Flow(
        APP_KEY,
        APP_SECRET,
        get_callback_url(),
        session,
        'dropbox-csrf-token')

def process_user(uid):
    token = redis_client.hget('tokens', uid)
    cursor = redis_client.hget('cursors', uid)

    client = DropboxClient(token)
    has_more = True

    while has_more:
        result = client.delta(cursor)

        for path, metadata in result['entries']:

            # Ignore deleted files, folders, and non-markdown files
            if metadata is None or metadata['is_dir'] or not path.endswith('.md'): continue

            # Convert to Markdown and store as <basename>.html
            html = markdown(client.get_file(path).read())
            client.put_file(path[:-3] + '.html', html, overwrite=True)

        # Update cursor
        cursor = result['cursor']
        redis_client.hset('cursors', uid, cursor)

        # Repeat only if there's more
        has_more = result['has_more']

def validate_request(message):
    '''Validate that the request is properly signed by Dropbox. (If not, this is a spoofed webhook.)'''

    return request.headers.get('X-Dropbox-Signature') == hmac.new(APP_SECRET, message, sha256).hexdigest()

@app.route('/')
def index():
    return render_template('index.html')
 
@app.route('/login')
def login():
    return redirect(get_flow().start())
 
@app.route('/oauth_callback')
def oauth_callback():
    '''Callback function for when the user returns from OAuth.'''

    access_token, uid, extras = get_flow().finish(request.args)
 
    # Extract and store the access token, user ID, and time zone.
    redis_client.hset('tokens', uid, access_token)

    process_user(uid)

    return redirect(url_for('done'))

@app.route('/done')
def done(): 
    return render_template('done.html')

@app.route('/webhook', methods=['GET'])
def challenge():
    # Make sure this is a valid request from Dropbox
    if not validate_request('dbx'): abort(403)

    return request.args.get('challenge')

@app.route('/webhook', methods=['POST'])
def webhook():
    # Make sure this is a valid request from Dropbox
    if not validate_request(request.data): abort(403)

    for uid in json.loads(request.data)['delta']['users']:
        process_user(uid)
    return ''
 
if __name__=='__main__':
    app.run(debug=True)
