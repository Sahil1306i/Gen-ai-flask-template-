from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
import openai
import os

app = Flask(__name__)

# Configurations
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/dbname')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
openai.api_key = os.getenv('OPENAI_API_KEY', 'your_openai_api_key')

jwt = JWTManager(app)
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Password should be hashed in a real implementation

class ReportData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.Text, nullable=False)

# Utility Functions
def get_user_data(user_id):
    return ReportData.query.filter_by(user_id=user_id).all()

def generate_report_from_spec(spec, data):
    # Implement actual report generation logic here
    return {"spec": spec, "data": [d.data for d in data]}

# Routes
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid username or password"}), 401

@app.route('/generate_report', methods=['POST'])
@jwt_required()
def generate_report():
    query = request.json.get('query')
    user_id = get_jwt_identity()

    try:
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=query,
            max_tokens=100
        )
        report_spec = response.choices[0].text
        return jsonify(report_spec=report_spec), 200
    except Exception as e:
        return jsonify({"msg": "Error generating report", "error": str(e)}), 500

@app.route('/compile_report', methods=['POST'])
@jwt_required()
def compile_report():
    report_spec = request.json.get('report_spec')
    user_id = get_jwt_identity()

    try:
        data = get_user_data(user_id)
        report = generate_report_from_spec(report_spec, data)
        return jsonify(report=report), 200
    except Exception as e:
        return jsonify({"msg": "Error compiling report", "error": str(e)}), 500

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
