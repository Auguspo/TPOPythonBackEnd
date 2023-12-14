import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from requests.exceptions import RequestException

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
    link = db.Column(db.String(500))

    def __init__(self, nombre, descripcion, imagen, fecha_horario, link):
        self.nombre = nombre
        self.descripcion = descripcion
        self.imagen = imagen
        self.fecha_horario = fecha_horario
        self.link = link

with app.app_context():
    db.create_all()

class EventSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "descripcion", "imagen", "fecha_horario", "link")

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
    link = request.json["link"]

    new_event = Event(nombre, descripcion, imagen, fecha_horario, link)
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
        event.link = request.json.get("link", event.link)

        db.session.commit()
        return event_schema.jsonify(event)
    else:
        return jsonify({"message": "Evento no encontrado"}), 404
@app.route("/scrape", methods=["GET"])
def scrap_and_update():
    try:
        # Borrar los datos existentes en la tabla 'events'
        with app.app_context():
            Event.query.delete()
            db.session.commit()

        # URL del sitio a scrappear
        url = "https://nbatv.site"  # Reemplaza con la URL correcta

        # Realizar la solicitud HTTP y obtener el contenido
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Verificar si la solicitud fue exitosa

        # Crear un objeto BeautifulSoup para analizar el HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Resto del código de scraping...
        data = []
        for row in soup.select('tr')[1:]:
            columns = row.find_all(['td', 'th'])
            hora = columns[0].find('span', class_='t').text.strip()
            imagen = columns[1].find('img')['src']
            
            # Guardar el texto dentro antes del tag <a>
            nombre_td = columns[2].find('td', align='left')
            if nombre_td:
                # Obtener el texto directamente del elemento td
                partido_text = nombre_td.get_text(strip=True)

                # Buscar el índice del carácter ":" en el texto
                index_colon = partido_text.find(':')

                # Verificar si se encontró el carácter ":" y extraer el nombre
                if index_colon != -1:
                    partido = partido_text[:index_colon].strip()
                else:
                    partido = partido_text
            else:
                partido = ""

            link = columns[2].find('a')
            if link:
                descripcion = link.b.text.strip()
                link = url + link['href']
            else:
                descripcion = ""
                link = ""

            # Almacenar la información en un diccionario
            entry = {
                'Hora': hora,
                'Imagen': imagen,
                'Partido': partido,
                'Descripcion': descripcion,
                'Enlace': link
            }

            # Agregar el diccionario a la lista de datos
            data.append(entry)

        # Aquí puedes actualizar tu base de datos o hacer lo que necesites con los datos
        with app.app_context():
            for entry in data:
                # Ensure the 'nombre' field does not exceed 100 characters
                nombre = entry['Partido'][:100]
                descripcion = entry['Descripcion'][:300]
                imagen = entry['Imagen'][:400]
                fecha_horario = entry['Hora'][:20]
                link = entry['Enlace'][:500]

                db.session.add(Event(nombre=nombre, descripcion=descripcion, imagen=imagen, fecha_horario=fecha_horario, link=link))
            db.session.commit()

        # Retorna una respuesta para indicar el éxito del scraping
        return jsonify({"message": "Web scraping y actualización exitosos."})
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 403:
            return jsonify({"error": "Error 403 Forbidden: Acceso denegado al recurso."}), 403
        else:
            return jsonify({"error": f"Error HTTP: {http_err}"}), 500
    except RequestException as e:
        return jsonify({"error": f"Error en la solicitud: {e}"}
        )
# Llamar a la función para probar
if __name__ == "__main__":
    app.run(debug=True, port=5000)
