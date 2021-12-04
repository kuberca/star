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
    unresolved = get_server().results.get_all_unresolved()
    sorted_unresolved = sorted(unresolved, key=lambda it: it.count, reverse=True)
    return render_template('result/index.html', unresolved=sorted_unresolved)

@bp.route('/resolved')
def resolved():
    resolved = get_server().results.get_all_resolved()
    sorted_resolved = sorted(resolved, key=lambda it: it.count, reverse=True)
    return render_template('result/resolved.html', resolved=sorted_resolved)

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    is_resolved = request.args.get('resolved')
    context_id = request.args.get('context_id')
    if is_resolved == "1":
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



@bp.route('/groups')
def groups():
    groups = get_server().results.get_all_unresolved_groups()
    sorted_groups = sorted(groups, key=lambda it: it.count, reverse=True)
    resolved_groups = get_server().results.get_all_resolved_groups()
    sorted_resolved_groups = sorted(resolved_groups, key=lambda it: it.count, reverse=True)
    summary = {}
    for group in sorted_groups:
        if group.error_type not in summary:
            summary[group.error_type] = [(group.group_id, group.count)]
        else:
            summary[group.error_type].append((group.group_id, group.count))
        
    for group in sorted_resolved_groups:
        if group.error_type not in summary:
            summary[group.error_type] = [(group.group_id, group.count)]
        else:
            summary[group.error_type].append((group.group_id, group.count))

    return render_template('result/groups.html', groups=sorted_groups, resolved_groups=sorted_resolved_groups, summary=summary)

@bp.route('/cleanup')
def cleanup():
    get_server().results.cleanup()
    return render_template('result/index.html', unresolved=[])


@bp.route('/<int:id>/group_update', methods=('GET', 'POST'))
def group_update(id):
    is_resolved = request.args.get('resolved')
    if is_resolved is None or is_resolved == "0":
        group = get_server().results.get_unresolved_group(id)
    else:
        group = get_server().results.get_resolved_group(id)

    if request.method == 'GET':
        return render_template('result/group_update.html', group=group)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == "extract":
            # extract result from group, still show current group info
            result_id = request.form.get('result_id')
            context_id = request.form.get('context_id')
            result = get_unresolved(result_id, context_id)
            get_server().results.split_result_from_group(result)
            group = get_server().results.get_unresolved_group(id)
            return render_template('result/group_update.html', group=group)
        elif action == "merge":
            # reverse operation of extract, we need to remove the manual_group flag
            # of the group, to make it able to be merged again
            # result_id = request.form.get('result_id')
            # context_id = request.form.get('context_id')
            # result = get_unresolved(result_id, context_id)
            # get_server().results.split_result_from_group(result)
            group = get_server().results.get_unresolved_group(id)
            get_server().results.set_group_unmanual(group)
            return redirect(url_for('result.groups'))
        else:
            analysis = request.form['analysis']
            label = request.form['label']
            error_type = request.form['error_type']
            group.analysis = analysis
            group.label = label
            group.error_type = error_type
            get_server().results.resolve_group(group)

            return redirect(url_for('result.groups'))

    



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

        result_scores = {}
        # compute similarity between all results of from_group
        for i in range(len(group.results)):
            for j in range(i+1, len(group.results)):
                r1 = group.results[i]
                r2 = group.results[j]
                s = get_server().results.get_result_sim_score(r1, r2)
                result_scores[(r1.template_id, r2.template_id)] = (s,)

        return render_template('result/group_compare_result.html', group=group, to_group=to_group, groups=groups, 
            score=score, scores=scores, result_scores=result_scores)
    
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