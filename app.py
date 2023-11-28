from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/proyecto"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Canal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    numero = db.Column(db.Integer)
    emisora = db.Column(db.String(100))
    imagen = db.Column(db.String(400))

    def __init__(self, nombre, numero, emisora, imagen):
        self.nombre = nombre
        self.numero = numero
        self.emisora = emisora
        self.imagen = imagen

with app.app_context():
    db.create_all()

class CanalSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "numero", "emisora", "imagen")

canal_schema = CanalSchema()
canales_schema = CanalSchema(many=True)

@app.route("/canales", methods=["GET"])
def get_canales():
    all_canales = Canal.query.all()
    result = canales_schema.dump(all_canales)
    return jsonify(result)

@app.route("/canales/<id>", methods=["GET"])
def get_canal(id):
    canal = Canal.query.get(id)
    return canal_schema.jsonify(canal)

@app.route("/canales/<id>", methods=["DELETE"])
def delete_canal(id):
    canal = Canal.query.get(id)
    db.session.delete(canal)
    db.session.commit()
    return canal_schema.jsonify(canal)

@app.route("/canales", methods=["POST"])
def create_canal():
    nombre = request.json["nombre"]
    numero = request.json["numero"]
    emisora = request.json["emisora"]
    imagen = request.json["imagen"]
    new_canal = Canal(nombre, numero, emisora, imagen)
    db.session.add(new_canal)
    db.session.commit()
    return canal_schema.jsonify(new_canal)

@app.route("/canales/<id>", methods=["PUT"])
def update_canal(id):
    canal = Canal.query.get(id)
    canal.nombre = request.json["nombre"]
    canal.numero = request.json["numero"]
    canal.emisora = request.json["emisora"]
    canal.imagen = request.json["imagen"]
    db.session.commit()
    return canal_schema.jsonify(canal)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
