from flask import Flask

app = Flask(__name__,
            static_url_path='',
            static_folder='web/static',
            template_folder='web/templates'
            )
app.debug = True

import flask_web_app.routes


app.run()
