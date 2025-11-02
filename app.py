from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave_secreta"  # necesaria para mensajes flash
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mi_base.db'  # base de datos única
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from gtts import gTTS
import qrcode, os, datetime

# --- CONFIGURACIÓN GENERAL ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['AUDIO_FOLDER'] = 'static/audio'

db = SQLAlchemy(app)

# --- MODELOS ---
class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    dni = db.Column(db.String(20))
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(100))

class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255))
    imagen = db.Column(db.String(255))
    mapa = db.Column(db.String(255))

with app.app_context():
    db.create_all()

# --- RUTAS ---
@app.route('/')
def index():
    return render_template('index.html')

# ----- Módulo Personas -----
@app.route('/personas', methods=['GET', 'POST'])
def personas():
    if request.method == 'POST':
        p = Persona(
            nombre=request.form['nombre'],
            dni=request.form['dni'],
            telefono=request.form['telefono'],
            correo=request.form['correo']
        )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('personas'))
    personas = Persona.query.all()
    return render_template('personas.html', personas=personas)

@app.route('/eliminar_persona/<int:id>')
def eliminar_persona(id):
    p = Persona.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('personas'))

# ----- Módulo Comunicados -----
@app.route('/comunicados', methods=['GET', 'POST'])
def comunicados():
    mensaje_generado = None
    if request.method == 'POST':
        texto = request.form['texto']
        if texto.strip():
            nombre_audio = f"comunicado_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
            ruta_audio = os.path.join(app.config['AUDIO_FOLDER'], nombre_audio)
            tts = gTTS(text=texto, lang='es')
            tts.save(ruta_audio)
            mensaje_generado = nombre_audio
    return render_template('comunicados.html', mensaje=mensaje_generado)

# ----- Módulo QR -----
@app.route('/qrcodes', methods=['GET', 'POST'])
def qrcodes():
    if request.method == 'POST':
        texto = request.form['texto']
        mapa = request.files.get('mapa')
        nombre_qr = f"qr_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        ruta_qr = os.path.join(app.config['UPLOAD_FOLDER'], nombre_qr)
        img = qrcode.make(texto)
        img.save(ruta_qr)

        nombre_mapa = None
        if mapa and mapa.filename:
            nombre_mapa = mapa.filename
            mapa.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_mapa))

        nuevo_qr = QRCode(texto=texto, imagen=nombre_qr, mapa=nombre_mapa)
        db.session.add(nuevo_qr)
        db.session.commit()
        return redirect(url_for('qrcodes'))

    qrs = QRCode.query.all()
    return render_template('qrcodes.html', qrs=qrs)

@app.route('/eliminar_qr/<int:id>')
def eliminar_qr(id):
    qr = QRCode.query.get_or_404(id)
    db.session.delete(qr)
    db.session.commit()
    return redirect(url_for('qrcodes'))

# --- EJECUCIÓN ---
if __name__ == '__main__':
    os.makedirs('static/audio', exist_ok=True)
    os.makedirs('static/img', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)


# TABLA PERSONAS
class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20))
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(100))
    comunicados = db.relationship('Comunicado', backref='solicitante', lazy=True)

# TABLA COMUNICADOS
class Comunicado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    solicitante_id = db.Column(db.Integer, db.ForeignKey('persona.id'), nullable=False)
    area = db.Column(db.String(100))
    fecha = db.Column(db.Date, default=datetime.today)
    repeticiones = db.Column(db.Integer, default=1)
    archivo_audio = db.Column(db.String(200))  # nombre del archivo mp3

# TABLA QR
class CodigoQR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    contenido = db.Column(db.Text)
    imagen = db.Column(db.String(200))  # ruta de imagen QR

