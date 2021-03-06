import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
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
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    # try:
        # try to query model for all drinks
        results = Drink.query.all()
        # create an array with list of drinks
        # with short() representation of the model
        drinks = [Drink.short(r) for r in results]
        # return jsonified response and status code 200
        return jsonify({"success": False, "drinks": drinks}), 200
    # except BaseException:
        #abort(422)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
     where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    print(payload)
    try:
        # try to query model for all drinks
        results = Drink.query.all()
        # create an array with list of drinks
        # with short() representation of the model
        drinks = [Drink.long(r) for r in results]
        # return jsonified response and status code 200
        return jsonify({"success": False, "drinks": drinks}), 200
    except BaseException:
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    try:
        # extract drink title and recipe
        # from request body
        body = request.get_json()
        title = body.get('title')
        recipe = json.dumps(body.get('recipe'))
        # create object with request values
        new_drink = Drink(title=title, recipe=recipe)
        # insert new record in database
        Drink.insert(new_drink)
        # return jsonified request status code
        # and new drink
        drink = [new_drink.long()]
        return jsonify({"success": True, "drinks": drink}), 200
    except BaseException:
         abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
     where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):
    if id is None:
        abort(404)
    # get the drink of the database
    result = Drink.query.get(id)
    # it is not found abort
    if result is None:
        abort(404)
    # extract drink title and recipe
    # from request body
    try:
        body = request.get_json()
        title = body.get('title')
        recipe = json.dumps(body.get('recipe'))
        # udpate drink attributes
        result.title = title
        result.recipe = recipe
        # update drink in database
        Drink.update(result)
        # change to long respresentation
        drink = [result.long()]
        # return jsonified request status code
        # and new drink
        return jsonify({"success": True, "drinks": drink}), 200
    except BaseException:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    if id is None:
        abort(404)
    # get the drink of the database
    drink = Drink.query.get(id)
    # it is not found abort
    if drink is None:
        abort(404)
    # extract drink title and recipe
    # from request body
    try:
        drink.delete()
        return jsonify({"success": True, "delete": id}), 200
    except BaseException:
        abort(422)


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


@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "bad request"
                    }), 400


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
@app.errorhandler(AuthError)
def resource_not_found(error):
    jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }),


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Not authorized"
    }), 401
