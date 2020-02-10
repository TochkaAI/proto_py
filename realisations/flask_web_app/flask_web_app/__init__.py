from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from routes import routes as blueprint_routes
from auth import auth as blueprint_auth


app = Flask(__name__,
            static_url_path='',
            static_folder='web/static',
            template_folder='web/templates'
            )
app.debug = True

app.config.from_object('config')
db = SQLAlchemy(app)


app.register_blueprint(blueprint_auth)
app.register_blueprint(blueprint_routes)
app.run()
