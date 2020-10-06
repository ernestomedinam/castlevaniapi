from flask import Flask
from flask_migrate import Migrate
from src.models import db, Donante, Perfil, Visita
import json
import os

# iniciar la aplicación
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# iniciar la sesión de sqlalchemy - mysql
MIGRATE = Migrate(app, db)
db.init_app(app)
with app.app_context():
    # cargar data de un archivo .json con la información de los objetos a crear
    with open("./baseline_data.json") as data_file:
        data = json.load(data_file)
        # crear esos objetos y guardar en bdd
        for donante in data["donantes"]:
            nuevo_donante = Donante.registrarse(
                donante["cedula"],
                donante["nombre"],
                donante["apellido"],
                donante["password"]
            )
            db.session.add(nuevo_donante)
            try:
                db.session.commit()
                nuevo_perfil = Perfil.crear(nuevo_donante.id)
                db.session.add(nuevo_perfil)
                try:
                    db.session.commit()
                    nuevo_perfil.actualizar_perfil(donante["perfil"])
                    try:
                        db.session.commit()
                    except Exception as error: # actualizar_perfil failed
                        db.session.rollback()
                        print(f"ay caramba...{type(error)}:{error.args}")
                        db.session.delete(nuevo_donante)
                        db.session.delete(nuevo_perfil)
                        db.session.commit()
                except Exception as error: # nuevo_perfil commit failed
                    db.session.rollback()
                    print(f"ay caramba...{type(error)}:{error.args}")
                    db.session.delete(nuevo_donante)
                    db.session.commit()
            except Exception as error: # nuevo_donante commit failed
                db.session.rollback()
                print(f"ay caramba...{type(error)}:{error.args}")
