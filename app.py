from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(_name_)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://Multitude6788:6y22ayv9y6h7yc@Multitude6788.mysql.pythonanywhere-services.com/Multitude6788$proyecto"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.String(300))
    imagen = db.Column(db.String(400))
    fecha_horario = db.Column(db.String(20)) 

    def _init_(self, nombre, descripcion, imagen, fecha_horario):
        self.nombre = nombre
        self.descripcion = descripcion
        self.imagen = imagen
        self.fecha_horario = fecha_horario 
with app.app_context():
    db.create_all()

class EventSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "descripcion", "imagen", "fecha_horario")

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
    fecha_horario = request.json["fecha_horario"]  

    new_event = Event(nombre, descripcion, imagen, fecha_horario)
    db.session.add(new_event)
    db.session.commit()
    return event_schema.jsonify(new_event)

@app.route("/events/<id>", methods=["PUT"])
def update_event(id):
    event = Event.query.get(id)

    if event:
        event.nombre = request.json.get("nombre", event.nombre)
        event.descripcion = request.json.get("descripcion", event.descripcion)
        event.imagen = request.json.get("imagen", event.imagen)
        event.fecha_horario = request.json.get("fecha_horario", event.fecha_horario)

        db.session.commit()
        return event_schema.jsonify(event)
    else:
        return jsonify({"message": "Evento no encontrado"}), 404

if _name_ == "_main_":
    app.run(debug=True, port=5000)