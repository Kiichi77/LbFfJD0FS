import flask
from pymongo import MongoClient
import socket
from os import getenv
from flask import Flask, request, render_template, redirect, url_for, abort
from string import digits, ascii_letters
from secrets import choice

baseurl = ''
baseurl_var = getenv('BASEURL')
if not baseurl_var :
    hostname = socket.gethostname()
    baseurl = socket.gethostbyname(hostname)
else:
    baseurl = baseurl_var
max_redirect_len = 9
alphabet = digits + ascii_letters
mongo_client = MongoClient('db',
                           username=getenv('MONGO_INITDB_ROOT_USERNAME'),
                           password=getenv('MONGO_INITDB_ROOT_PASSWORD'))
db = mongo_client['shorten_url']
redirects = db.redirects
app = Flask(__name__, template_folder='/webapp/assets/')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<path:path>', methods=['GET'])
def path_redirect(path):
    global redirects
    redirect_path = redirects.find_one({'shortenUrl': path})
    if not redirect_path:
        return render_template('404.html')
    else:
        return redirect(redirect_path['actualUrl'], code=301)


@app.route('/newurl', methods=['POST'])
def register_path():
    global max_redirect_len
    global redirects
    json_data = request.get_json()
    shortenUrl, actualUrl = None, None
    try:
        actualUrl = json_data['url']
    except:
        abort(500, description='Invalid parameters provided')
    if actualUrl[:7] != 'http://' and actualUrl[:8] != 'https://':
        abort(400, description='Invalid URL scheme provided')
    existing_redirect = redirects.find_one({'actualUrl': actualUrl})
    if existing_redirect:
        return f'{{url={actualUrl}, shortenUrl=http://{baseurl}/{existing_redirect["shortenUrl"]}}}'
    else:
        shortenUrl = ''.join([choice(alphabet) for i in range(max_redirect_len)])
        while redirects.find_one({'shortenUrl': shortenUrl}):
            shortenUrl = ''.join([choice(alphabet) for i in range(max_redirect_len)])
        redirects.insert_one({'shortenUrl': shortenUrl, 'actualUrl': actualUrl})
        existing_redirect = redirects.find_one({'actualUrl': actualUrl})
    return f'{{url={actualUrl}, shortenUrl=http://{baseurl}/{existing_redirect["shortenUrl"]}}}'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)