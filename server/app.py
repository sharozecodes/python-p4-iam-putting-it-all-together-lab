#!/usr/bin/env python3

from flask import request, session, make_response, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        
        json = request.get_json()
        if 'username' in json and 'password' in json:
            user = User(
                username=json['username'],
                image_url=json.get('image_url'),
                bio=json.get('bio')
            )
            user.password_hash = json['password']
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id

            return user.to_dict(), 201
        else:
            return {'error': 'unprocessable entity'}, 422
        
class CheckSession(Resource):
    def get(self):
        if session.get('user_id') == None:
            return {'error': 'Unauthorized'}, 401
        else:
            user = User.query.filter_by(id=session.get('user_id')).first()
            return user.to_dict(), 200

class Login(Resource):
    def post(self):
        username = request.get_json()['username']
        user = User.query.filter_by(username=username).first()
        password = request.get_json()['password']

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        else:
            return {'error': 'Invalid username/password'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        else:
            return {'error':'unauthorized'}, 401
        
class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id') == None:
            return {'errors': 'unauthorized'}, 401
        else:
            recipes = [recipe.to_dict() for recipe in Recipe.query.all()]
            return recipes, 200
        
    def post(self):
        if session.get('user_id') == None:
            return {'errors': ['unauthorized']}, 401
        else:
            json = request.get_json()
            if 'title' in json and 'instructions' in json and 'minutes_to_complete' in json and len(json['instructions']) >= 50:
                recipe = Recipe(
                    title=json['title'],
                    instructions=json['instructions'],
                    minutes_to_complete=json['minutes_to_complete'],
                    user_id=session.get('user_id')
                )
                db.session.add(recipe)
                db.session.commit()
                return recipe.to_dict(), 201
            else:
                return {}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
