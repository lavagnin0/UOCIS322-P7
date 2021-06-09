from flask import Flask, request, render_template, Response
from flask_restful import Resource, Api
import pymongo
from pymongo import MongoClient
import os
import flask
from itsdangerous import (TimedJSONWebSignatureSerializer \
                              as Serializer, BadSignature, \
                          SignatureExpired)
from passlib.apps import custom_app_context as pwd_context

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.tododb
authdb = client.authdb

DEFAULT_SORT = [('dist', pymongo.ASCENDING)]
SECRET_KEY = 'test1234@#$'


def verify_auth_token(token):
    s = Serializer(SECRET_KEY)
    try:
        data = s.loads(token)
        if authdb.authdb.find(data) is not None:
            return "Success"
        else:
            raise BadSignature
    except SignatureExpired:
        return "Expired token!"    # valid token, but expired
    except BadSignature:
        return "Invalid token!"    # invalid token


class ListAll(Resource):
    def get(self, dtype=''):
        token = request.args.get('token', type=str)
        if token is None or verify_auth_token(token) != "Success":
            return Response('Invalid token', 401)
        k = request.args.get('top', default=0, type=int)
        data = list(db.tododb.find({}, {'_id': 0, 'open': 1, 'close': 1}, sort=DEFAULT_SORT, limit=k))
        if dtype == 'csv':
            response = "Open,Close\n"
            for item in data:
                response += item['open'] + ',' + item['close'] + '\n'
            return response
        return flask.jsonify(data)


class ListOnlyOpen(Resource):
    def get(self, dtype=''):
        token = request.args.get('token', type=str)
        if token is None or verify_auth_token(token) != "Success":
            return Response('Invalid token', 401)
        k = request.args.get('top', default=0, type=int)
        data = list(db.tododb.find({}, {'_id': 0, 'open': 1}, sort=DEFAULT_SORT, limit=k))
        if dtype == 'csv':
            response = "Open\n"
            for item in data:
                response += item['open'] + '\n'
            return response
        return flask.jsonify(data)


class ListOnlyClose(Resource):
    def get(self, dtype=''):
        token = request.args.get('token', type=str)
        if token is None or verify_auth_token(token) != "Success":
            return Response('Invalid token', 401)
        k = request.args.get('top', default=0, type=int)
        data = list(db.tododb.find({}, {'_id': 0, 'close': 1}, sort=DEFAULT_SORT, limit=k))
        if dtype == 'csv':
            response = "Close\n"
            for item in data:
                response += item['close'] + '\n'
            return response
        return flask.jsonify(data)


class Register(Resource):
    def post(self):
        username = request.args.get('username', '', type=str)
        password = request.args.get('password', '', type=str)

        if username is None or password is None:
            return Response('No username or password provided', 400)
        if authdb.authdb.find_one({'username': username}) is not None:
            return Response('Username already taken', 400)
        hashed = pwd_context.encrypt(password)
        authdb.authdb.insert_one({'username': username, 'password': hashed})

        return Response('Successfully registered user {}'.format(username), 201)


class Token(Resource):
    def get(self):
        username = request.args.get('username', '', type=str)
        password = request.args.get('password', '', type=str)

        if username is None or password is None:
            return Response('No username or password provided', 400)
        user = authdb.authdb.find_one({'username': username})
        if user is None:
            return Response('Username invalid', 401)
        hashed = user.get('password') 
        if not pwd_context.verify(password, hashed):
            return Response('Password invalid', 401)
        s = Serializer(SECRET_KEY, expires_in=600)
        token = s.dumps(user.get('_id'))

        return flask.jsonify({'token': token.decode('utf-8'), 'duration': 600}), 200


api.add_resource(ListAll, '/listAll', '/listAll/<string:dtype>')
api.add_resource(ListOnlyOpen, '/listOpenOnly', '/listOpenOnly/<string:dtype>')
api.add_resource(ListOnlyClose, '/listCloseOnly', '/listCloseOnly/<string:dtype>')
api.add_resource(Register, '/register')
api.add_resource(Token, '/token')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
