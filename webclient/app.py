import json
import io
from flask import Flask, request, render_template, jsonify
from thugworker.thugtask import check_url

with io.open('../config.json', encoding='utf8') as f:
    config = json.load(f)

app = Flask(__name__)
app.config.update(config)

tasks = list()
# tasks.append(('id', 'url', 'agent', 'status', 'checked_date'))


@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)


@app.route('/thugtask', methods=['POST'])
def thugtask():
    data = {}
    json_data = json.loads(request.data)

    for entry in json_data:
        data.setdefault(entry['name'], []).append(entry['value'])

    if len(data['url']) <= 0:
        return jsonify({}), 400

    if len(data['useragent']) <= 0:
        data['useragent'].append('winxpie60')

    for agent in data['useragent']:
        task = check_url.apply_async(args=[data['url'][0], agent])
        tasks.append((task.id, data['url'][0], agent))

    return jsonify({}), 202


@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = check_url.AsyncResult(task_id)

    response = {
        'state': task.state
    }

    return jsonify(response)


@app.route("/get_tasks")
def get_tasks():
    output = {
        'iTotalRecords': len(tasks),
        'iTotalDisplayRecords': len(tasks),
        'sEcho': str(int(request.values['sEcho'])),
        'aaData': []
    }

    for entry in tasks:
        output['aaData'].append(entry)

    return jsonify(output)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
