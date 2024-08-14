from flask import Flask
from config import Config
from db import db
from views.main import main_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)
