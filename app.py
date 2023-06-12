from flask import Flask, jsonify, make_response
import json

app = Flask(__name__)

@app.route("/test")
def testApiFunction(event, context):
    with app.app_context():
        message = "Hello world!"
        response = {
            "statusCode": 200,
            "body": json.dumps({"message": message})
        }
        return response

@app.route("/search")
def search(event, context):
    with app.app_context():
        message = "Hello world!"
        response = {
            "statusCode": 200,
            "body": json.dumps({"message": message})
        }
        return response

@app.route("/")
def hello_from_root():
    return jsonify(message='Hello from root!')


@app.route("/hello")
def hello():
    return jsonify(message='Hello from path!')

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
