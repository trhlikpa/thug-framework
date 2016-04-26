import json
from flask import Flask, request, session, render_template, redirect, url_for, flash
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import URL

from thugworker.thugtask import add

with open('../config.json') as f:
    config = json.load(f)

app = Flask(__name__)
app.config.update(config)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UrlForm()

    if request.method == 'POST':
        if form.validate():
            add.delay(form.url.data)

    return render_template('index.html', form=form)


class UrlForm(Form):
    url = StringField('url', validators=[URL()])
    submit = SubmitField("Send")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
