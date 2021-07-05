from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary
        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}

@app.route("/")
def home():
    return render_template("index.html")

## HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    cafes_data = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes_data)
    return jsonify(cafes=random_cafe.to_dict())
'''


# Above is simpler way to use jsonify() compared to below lenghty code
# <Serialising DB row Object to JSON>
# by first converting to dictionary and using jsonify() to convert the dictionary to a JSON.
# Cafe class includes 'to_dict' function.

    return jsonify(
        cafe={
        "name" : random_cafe.name,
        "map_url" : random_cafe.map_url,
        "img_url" : random_cafe.img_url,
        "location" : random_cafe.location,
        "seats" : random_cafe.seats,
        "has_toilet" : random_cafe.has_toilet,
        "has_wifi" : random_cafe.has_wifi,
        "has_sockets" : random_cafe.has_sockets,
        "can_take_calls" : random_cafe.can_take_calls,
        "coffee_price" : random_cafe.coffee_price
    })
'''
## HTTP GET - Read Record
@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    #This uses a List Comprehension but you could also split it into 3 lines.
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc") #url parameter e.g./search?loc=Peckham
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})

## HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price") #e.g. /update-price/1?new_price=£1.11
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})
    else:
        return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."})

## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key") #e.g. /report-closed/1?api-key=TopSecretAPIKey
    closed_cafe = db.session.query(Cafe).get(cafe_id)
    if closed_cafe and api_key == "TopSecretAPIKey":
        db.session.delete(closed_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully deleted the cafe."})
    elif closed_cafe and api_key != "TopSecretAPIKey":
        return jsonify(error={"error": "Sorry, that's not allowed. Make sure you have the correct api-key"})
    elif not closed_cafe:
        return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."})


if __name__ == '__main__':
    app.run(debug=True)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
