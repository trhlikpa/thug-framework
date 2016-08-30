from flask import Flask
from webclient import config

app = Flask(__name__)
app.config.update(config)

# Import blueprints
from webclient.api import api_blueprint

# Register blueprints
app.register_blueprint(api_blueprint)

# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
