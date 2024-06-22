from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import openai
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/dbname'
jwt = JWTManager(app)
db = SQLAlchemy(app)

# User and ReportData models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

class ReportData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.Text, nullable=False)

# Authentication
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    # Verify user credentials (e.g., query from database)
    if username == 'test' and password == 'test':  # Replace with real validation
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

# Generate report using Gen-AI
openai.api_key = 'your_openai_api_key'

@app.route('/generate_report', methods=['POST'])
@jwt_required()
def generate_report():
    query = request.json.get('query')
    user_id = get_jwt_identity()
    
    # Call to OpenAI API
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=query,
        max_tokens=100
    )
    
    report_spec = response.choices[0].text
    return jsonify(report_spec=report_spec), 200

# Compile report
@app.route('/compile_report', methods=['POST'])
@jwt_required()
def compile_report():
    report_spec = request.json.get('report_spec')
    user_id = get_jwt_identity()
    
    # Retrieve data for the user and compile report
    data = ReportData.query.filter_by(user_id=user_id).all()
    report = generate_report_from_spec(report_spec, data)
    
    return jsonify(report=report), 200

# Utility functions
def get_user_data(user_id):
    return ReportData.query.filter_by(user_id=user_id).all()

def generate_report_from_spec(spec, data):
    # Implement report generation logic here
    return {"spec": spec, "data": data}

# Run the application
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
