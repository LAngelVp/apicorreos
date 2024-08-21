from flask import Flask, request, jsonify
import configparser
import ssl
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

app = Flask(__name__)

# Configuración SSL para evitar problemas con certificados no verificados
ssl._create_default_https_context = ssl._create_unverified_context

# Leer configuración desde el archivo config.ini
config = configparser.ConfigParser()
# Obtener la ruta del directorio donde se encuentra el script actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta completa al archivo config.ini
config_path = os.path.join(current_dir, 'config.ini')
config.read(config_path)

# Función para enviar correo electrónico utilizando SendGrid
def send_mail_using_sendgrid(api_key, from_email, to_emails, subject, html_content):
    if api_key and from_email and to_emails:
        message = Mail(from_email, to_emails, subject, html_content)
        try:
            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            return {
                'status_code': response.status_code,
                'body': response.body,
                'headers': response.headers
            }
        except Exception as e:
            print(f"Error al enviar el correo: {e}")  # Imprimir error en consola
            return {'error': str(e)}
    return {'error': 'Invalid parameters'}

@app.route('/enviarcorreo', methods=['POST'])
def enviar_correo():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        settings = config["SETTINGS"]
        api_key = settings.get("APIKEY")
        from_email = settings.get("FROM")
        to_emails = settings.get("TO","")

        if not api_key or not from_email or not to_emails:
            return jsonify({'error': 'Configuration is missing some parameters'}), 500

        subject = data.get('asunto', 'No Subject')

        # Construir el contenido HTML con formato
        html_content = f"""
        Nombre del remitente : {data.get('nombre', '')}
        Correo de contacto : {data.get('email', '')}
        Numero de telefono para contactar : {data.get('numtelefono', '')}
        Asunto {data.get('asunto', '')}
        Motivo : 
        {data.get('contexto', '')}
        """

        response = send_mail_using_sendgrid(api_key, from_email, to_emails, subject, html_content)

        if 'error' in response:
            return jsonify(response), 500

        return jsonify({'message': 'Correo enviado exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
