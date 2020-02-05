from flask import Flask

app = Flask(__name__)
app.debug = True

import flask_web_app.routes


app.run()
