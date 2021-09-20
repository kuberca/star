from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from datetime import datetime

from backend.backend import Server

bp = Blueprint('result', __name__)

server = None

@bp.route('/')
def index():
    unresolved, resolved = get_results()
    return render_template('result/index.html', unresolved=unresolved, resolved=resolved)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    is_resolved = request.args.get('resolved')
    if is_resolved == "true":
        result = get_resolved(id)
    else:
        result = get_result(id)

    if request.method == 'POST':
        analysis = request.form['analysis']
        label = request.form['label']
        result.analysis = analysis
        result.label = label
        get_server().results.resolve(result)

        return redirect(url_for('index'))

    return render_template('result/update.html', result=result)


def get_result(id: int):
    return get_server().results.get_unresolved(id)

def get_resolved(id: int):
    return get_server().results.get_resolved(id)

def get_results():
    return get_server().results.get_all()

def get_server() -> Server:
    global server
    return server

def start_backend():
    print("start backend")
    global server
    cfg = {}
    cfg["drain3"]={"config_file":"drain3.ini", "persist_dir":"."}
    server = Server(config=cfg)
    server.start_in_gb()