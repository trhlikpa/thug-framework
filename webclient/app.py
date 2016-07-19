import io
import json
from flask import Flask

# load configuration
with io.open('../config.json', encoding='utf8') as f:
    config = json.load(f)

app = Flask(__name__)
app.config.update(config)

# Import task module
from webclient.api.tasks.controllers import tasks_blueprint
from webclient.api.jobs.controllers import jobs_blueprint

# Register blueprints
app.register_blueprint(tasks_blueprint)
app.register_blueprint(jobs_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
