#!/usr/bin/env python3

from flask import Flask, jsonify, make_response, request
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource

from models import db, Hero, Power, HeroPower

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///superheroes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

ma = Marshmallow(app)

# Schema Definitions

class PowerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Power
        fields = ('id', 'name', 'description')

power_schema = PowerSchema()
powers_schema = PowerSchema(many=True)
    
class HeroSchema(ma.SQLAlchemyAutoSchema):
    powers = ma.Nested(PowerSchema, many=True)
    
    class Meta:
        model = Hero
        fields = ('id', 'name', 'super_name')
        
hero_schema = HeroSchema()
heroes_schema = HeroSchema(many=True)

@app.route('/')
def index():
    return "Welcome to the Superhero API! Use /heroes and /powers to access heroes and powers data respectively."


# Resource Definitions

class Heroes(Resource):
    def get(self):
        response = heroes_schema.dump(Hero.query.all())
        return make_response(
            jsonify(response),
            200
        )

api.add_resource(Heroes, '/heroes')

class HeroesById(Resource):
    def get(self, id):
        hero = Hero.query.filter_by(id=id).first()
        if not hero:
            return make_response( jsonify({"error": "Hero not found"}), 404 )
        resp = hero_schema.dump(hero)
        return make_response(
            jsonify(resp),
            200
        )

api.add_resource(HeroesById, '/heroes/<int:id>')

class Powers(Resource):
    def get(self):
        response = powers_schema.dump(Power.query.all())
        return make_response(
            jsonify(response),
            200
        )

api.add_resource(Powers, '/powers')

class PowerById(Resource):
    
    def get(self, id):
        power = Power.query.filter_by(id=id).first()
        if not power:
            return make_response({"error": "Power not found"}, 404)
        response = power_schema.dump(power)
        return make_response(
            jsonify(response),
            200
        )

    def patch(self, id):
        power = Power.query.get(id)
        if not power:
            return make_response({"error": "Power not found"}, 404)

        description = request.json.get('description')
        if not description or len(description) < 20:
            return make_response({"errors": ["validation errors"]}, 400)
        
        power.description = description
        db.session.commit()
        
        response = power_schema.dump(power)
        return make_response(
            jsonify(response),
            200
        )

api.add_resource(PowerById, '/powers/<int:id>')

class HeroPowers(Resource):

    def post(self):
        strength = request.json.get('strength')
        power_id = request.json.get('power_id')
        hero_id = request.json.get('hero_id')
        
        if strength not in ['Strong', 'Weak', 'Average']:
            return make_response({"errors": ["validation errors"]}, 400)

        hero_power = HeroPower(strength=strength, power_id=power_id, hero_id=hero_id)
        db.session.add(hero_power)
        db.session.commit()

        hero = Hero.query.get_or_404(hero_id)
        resp = hero_schema.dump(hero)
        
        return make_response(
            jsonify(resp),
            201
        )

api.add_resource(HeroPowers, '/hero_powers')


if __name__ == '__main__':
    app.run(port=5555)