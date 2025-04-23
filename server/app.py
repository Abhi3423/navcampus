from flask import Flask, jsonify
from flask_cors import CORS
from routes.admin_routes import admin_bp
from routes.internalMap_routes import internal_map_bp
from routes.outerMap_routes import outer_map_bp

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"data": 'Welcome to Server.'}), 200

# Register API blueprints
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(internal_map_bp, url_prefix='/api')
app.register_blueprint(outer_map_bp, url_prefix='/api')  # unchanged external map routes

if __name__ == '__main__':
    app.run(debug=True)
