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

@bp.route('/<int:id>/detail')
def detail(id):
    is_resolved = request.args.get('resolved')
    context_id = request.args.get('context_id')
    if is_resolved == "true":
        result = get_resolved(id, context_id)
    else:
        result = get_unresolved(id, context_id)
    
    detail_contexts = get_server().batcher.get_result_detail_contexts(result)
    return render_template('result/detail.html', result=result, detail_contexts=detail_contexts)

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

@bp.route('/cleanup')
def cleanup():
    get_server().results.cleanup()
    return render_template('result/index.html', unresolved=[])


@bp.route('/<int:id>/group_update', methods=('GET', 'POST'))
def group_update(id):
    group = get_server().results.get_unresolved_group(id)

    if request.method == 'POST':
        analysis = request.form['analysis']
        label = request.form['label']
        group.analysis = analysis
        group.label = label
        get_server().results.resolve_group(group)

        return redirect(url_for('result.groups'))

    return render_template('result/group_update.html', group=group)



@bp.route('/group_compare', methods=('GET', 'POST'))
def group_compare():
    
    groups = get_server().results.get_all_unresolved_groups()
    if request.method == 'GET':
        from_group = request.args.get('from_group')
        group = get_server().results.get_unresolved_group(from_group)
    elif request.method == 'POST':
        from_group = request.form.get('from_group')
        group = get_server().results.get_unresolved_group(from_group)
        to_group_id = request.form['to_group']
        to_group = get_server().results.get_unresolved_group(to_group_id)
        score = get_server().results.get_group_sim_score(group, to_group)

        threshold = float(request.form['threshold'])


        # compute similarity between all groups
        groups = get_server().results.get_all_unresolved_groups()
        scores = {}
        for g in groups:
            for g2 in groups:
                if g.group_id < g2.group_id:
                     s = get_server().results.get_group_sim_score(g, g2)
                     if s > threshold:
                        scores[(g.group_id, g2.group_id)] = (s, g.results[0].input, g2.results[0].input)

        return render_template('result/group_compare_result.html', group=group, to_group=to_group, groups=groups, score=score, scores=scores)
    
    return render_template('result/group_compare.html', group=group, groups=groups)      

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
    cfg["drain3"]={"config_file":"drain3.ini", "persist_dir":".", "model_file":"model/star.cla.bin"}
    server = Server(config=cfg)
    server.start_in_bg()