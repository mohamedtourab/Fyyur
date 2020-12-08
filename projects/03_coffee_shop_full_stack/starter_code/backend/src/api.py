import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
db = setup_db(app)
CORS(app, resources={r"/*": {"origins": "*"}})
'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

# db_drop_and_create_all()


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
https://dev-xp43zlgl.eu.auth0.com/authorize?audience=coffeeshop&response_type=token&client_id=fIRIYyxWcC3mhXdq52TKKzV66GJk4yBG&redirect_uri=https://127.0.0.1:8080/login-result
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.order_by(Drink.id).all()
    if len(drinks) == 0:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(jwt):
    drinks = Drink.query.order_by(Drink.id).all()
    if len(drinks) == 0:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    })


'''@TODO implement endpoint POST /drinks it should create a new row in the drinks table it should require the 
'post:drinks' permission it should contain the drink.long() data representation returns status code 200 and json {
"success": True, "drinks": drink} where drink an array containing only the newly created drink or appropriate status 
code indicating reason for failure '''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    unchecked_question = request.get_json()
    if unchecked_question['title'] is None or unchecked_question['recipe'] is None:
        abort(401)
    drink = Drink(title=unchecked_question['title'], recipe=json.dumps(unchecked_question['recipe']))
    try:
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except exc.SQLAlchemyError:
        abort(422)
    finally:
        db.session.close()


'''@TODO implement endpoint PATCH /drinks/<id> where <id> is the existing model id it should respond with a 404 error 
if <id> is not found it should update the corresponding row for <id> it should require the 'patch:drinks' permission 
it should contain the drink.long() data representation returns status code 200 and json {"success": True, 
"drinks": drink} where drink an array containing only the updated drink or appropriate status code indicating reason 
for failure '''


@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
    unchecked_question = request.get_json()
    if unchecked_question['title'] is None:
        abort(401)
    drink.title = unchecked_question['title']
    try:
        drink.update()
        return jsonify({"success": True, "drinks": [drink.long()]})
    except exc.SQLAlchemyError:
        db.session.rollback()
    finally:
        db.session.close()


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete()
        return jsonify({"success": True, "delete": drink_id})
    except exc.SQLAlchemyError:
        db.session.rollback()
    finally:
        db.session.close()


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handle_auth_error(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response
