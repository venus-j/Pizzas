#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurants_list = [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants]

    response = make_response(jsonify(restaurants_list), 200)
    return response

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        response = make_response(jsonify(restaurant.to_dict()), 200)
    else:
        response = make_response(jsonify({"error": "Restaurant not found"}), 404)
    return response

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        response = make_response('', 204)
    else:
        response = make_response(jsonify({"error": "Restaurant not found"}), 404)
    return response

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_list = [
        {
            'id': pizza.id,
            'name': pizza.name,
            'ingredients': pizza.ingredients
        }
        for pizza in pizzas
    ]
    response = make_response(jsonify(pizzas_list), 200)
    return response

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        new_restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        response = make_response(jsonify(new_restaurant_pizza.to_dict()), 201)
    except ValueError as e:
        response = make_response(jsonify({"errors": [str(e)]}), 400)
    except Exception as e:
        response = make_response(jsonify({"errors": ["An error occurred: " + str(e)]}), 500)
    return response

if __name__ == "__main__":
    app.run(port=5555, debug=True)