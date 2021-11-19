from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort
from datetime import datetime

from backend.backend import Server

bp = Blueprint('result', __name__)

server = None

UPLOAD_FOLDER = "/tmp"


@bp.route('/')
def index():
    unresolved, resolved = get_results()
    sorted_unresolved = sorted(unresolved, key=lambda it: it.count, reverse=True)
    return render_template('result/index.html', unresolved=sorted_unresolved)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    is_resolved = request.args.get('resolved')
    context_id = request.args.get('context_id')
    if is_resolved == "true":
        result = get_resolved(id, context_id)
    else:
        result = get_unresolved(id, context_id)

    if request.method == 'POST':
        analysis = request.form['analysis']
        label = request.form['label']
        result.analysis = analysis
        result.label = label
        get_server().results.resolve(result)

        return redirect(url_for('index'))

    return render_template('result/update.html', result=result)


@bp.route('/upload', methods=('GET', 'POST'))
def upload():

    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        fullfile=os.path.join(UPLOAD_FOLDER, filename)
        file.save(fullfile)
        get_server().start_batch_in_bg(fullfile)

        return redirect(url_for('index'))

    return render_template('result/upload.html')

@bp.route('/templates')
def templates():
    templates = get_server().preper.get_templates()
    return render_template('result/logtpl.html', templates=templates)

@bp.route('/resolved')
def resolved():
    unresolved, resolved = get_results()
    sorted_resolved = sorted(resolved, key=lambda it: it.count, reverse=True)
    return render_template('result/resolved.html', resolved=sorted_resolved)

@bp.route('/groups')
def groups():
    groups = get_server().results.get_all_unresolved_groups()
    sorted_groups = sorted(groups, key=lambda it: it.count, reverse=True)
    return render_template('result/groups.html', groups=sorted_groups)


@bp.route('/<int:id>/update_group', methods=('GET', 'POST'))
def update_group(id):
    group = get_server().results.get_unresolved_group(id)

    if request.method == 'POST':
        analysis = request.form['analysis']
        label = request.form['label']
        group.analysis = analysis
        group.label = label
        get_server().results.resolve_group(group)

        return redirect(url_for('result.groups'))

    return render_template('result/update_group.html', group=group)


def get_unresolved(id: int, context_id: str):
    return get_server().results.get_unresolved(id, context_id)

def get_resolved(id: int, context_id: str):
    return get_server().results.get_resolved(id, context_id)

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
    server.start_in_bg()