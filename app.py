from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Cargar variables de entorno (.env)
load_dotenv()

app = Flask(__name__)
CORS(app)

# ── Configuración de Flask-Mail para Gmail ────────────────────────────────────
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('GMAIL_USER'),
    MAIL_PASSWORD=os.getenv('GMAIL_APP_PASS'),
    MAIL_DEFAULT_SENDER=os.getenv('GMAIL_USER')
)

mail = Mail(app)

# Ruta de diagnóstico para comprobar credenciales
@app.route('/debug', methods=['GET'])
def debug_env():
    return jsonify({
        'GMAIL_USER': 'CARGADA' if app.config['MAIL_USERNAME'] else 'NO CARGADA',
        'GMAIL_APP_PASS': 'CARGADA' if app.config['MAIL_PASSWORD'] else 'NO CARGADA'
    })

def send_mail_with_gmail(recipients, subject, html_content):
    """Envía un correo con Gmail SMTP usando Flask-Mail."""
    try:
        msg = Message(subject, recipients=[recipients], html=html_content)
        mail.send(msg)
        return {'status': 'sent'}
    except Exception as e:
        return {'error': str(e)}

@app.route('/enviarcorreo', methods=['POST'])
def enviar_correo():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibió información'}), 400

    # Campos del formulario (con valores por defecto legibles)
    nombre      = data.get('nombre', 'Sin nombre')
    email       = data.get('email', 'Sin correo')
    numtelefono = data.get('numtelefono', 'Sin número')
    asunto      = data.get('asunto', 'Sin asunto')
    contexto    = data.get('contexto', 'Sin contenido')

    # Construir cuerpo HTML
    html_content = f"""
    <html>
      <body>
        <h2>Nuevo mensaje desde la web</h2>
        <p><strong>Nombre del remitente:</strong> {nombre}</p>
        <p><strong>Correo de contacto:</strong> {email}</p>
        <p><strong>Número telefónico:</strong> {numtelefono}</p>
        <p><strong>Asunto:</strong> {asunto}</p>
        <hr>
        <p><strong>Mensaje:</strong></p>
        <p>{contexto}</p>
      </body>
    </html>
    """

    # Destinatario: fija uno por defecto o toma uno del frontend
    destinatario = os.getenv('DESTINATARIO', app.config['MAIL_USERNAME'])

    result = send_mail_with_gmail(destinatario, asunto, html_content)

    if 'error' in result:
        return jsonify({'error': f"Error al enviar correo: {result['error']}"}), 500

    return jsonify({'message': 'Correo enviado exitosamente'}), 200

if __name__ == '__main__':
    # En producción crea un WSGI detrás de Gunicorn/uWSGI; debug solo en local
    app.run(debug=True)
