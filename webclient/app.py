import json

import sys
from flask import Flask, request, render_template, jsonify, url_for
from thugworker.thugtask import add

with open('../config.json') as f:
    config = json.load(f)

app = Flask(__name__)
app.config.update(config)

tasks = list()


@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)


@app.route('/thugtask', methods=['POST'])
def thugtask():
    data = {}
    json_data = json.loads(request.data)

    for entry in json_data:
        data.setdefault(entry['name'], []).append(entry['value'])

    return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=1)}


@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = add.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
