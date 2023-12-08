from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/proyecto"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.String(300))
    imagen = db.Column(db.String(400))
    link = db.Column(db.String(200))
    fecha_horario = db.Column(db.DateTime)  # Cambiado a DateTime

    def __init__(self, nombre, descripcion, imagen, link, fecha_horario):
        self.nombre = nombre
        self.descripcion = descripcion
        self.imagen = imagen
        self.link = link
        self.fecha_horario = fecha_horario

with app.app_context():
    db.create_all()

class EventSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "descripcion", "imagen", "link", "fecha_horario")

event_schema = EventSchema()
events_schema = EventSchema(many=True)

@app.route("/events", methods=["GET"])
def get_events():
    all_events = Event.query.all()
    result = events_schema.dump(all_events)
    return jsonify(result)

@app.route("/events/<id>", methods=["GET"])
def get_event(id):
    event = Event.query.get(id)
    return event_schema.jsonify(event)

@app.route("/events/<id>", methods=["DELETE"])
def delete_event(id):
    event = Event.query.get(id)
    db.session.delete(event)
    db.session.commit()
    return event_schema.jsonify(event)

@app.route("/events", methods=["POST"])
def create_event():
    nombre = request.json["nombre"]
    descripcion = request.json["descripcion"]
    imagen = request.json["imagen"]
    link = request.json["link"]
    fecha_horario_str = request.json["fecha_horario"]

    # Parsea la cadena de fecha y hora a un objeto DateTime
    fecha_horario = datetime.strptime(fecha_horario_str, "%d/%m/%Y %H:%M")

    new_event = Event(nombre, descripcion, imagen, link, fecha_horario)
    db.session.add(new_event)
    db.session.commit()
    return event_schema.jsonify(new_event)

@app.route("/events/<id>", methods=["PUT"])
def update_event(id):
    event = Event.query.get(id)
    event.nombre = request.json["nombre"]
    event.descripcion = request.json["descripcion"]
    event.imagen = request.json["imagen"]
    event.link = request.json["link"]
    event.fecha_horario = datetime.strptime(request.json["fecha_horario"], "%d/%m/%Y %H:%M")

    db.session.commit()
    return event_schema.jsonify(event)

if __name__ == "__main__":
    app.run(debug=True, port=5000)