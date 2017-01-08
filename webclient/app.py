from flask import Flask, render_template

app = Flask(__name__, static_folder='./frontend/static', template_folder='./frontend')
app.config.from_object('config')

# Import blueprints
from webclient.api import api_blueprint

# Register blueprints
app.register_blueprint(api_blueprint)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/<path:path>', methods=['GET'])
def any_path(path):
    return render_template('index.html')


# Run server
if __name__ == '__main__':
    app.run()
