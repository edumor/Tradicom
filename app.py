from flask import Flask, request, render_template, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from threading import Thread

# Recuperar las variables de entorno
load_dotenv()

# Debugging: Print environment variables
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST_USER = os.getenv('USER')
EMAIL_HOST_PASSWORD = os.getenv('PASSWORD')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_DESTINATARIO = os.getenv('DESTINATARIO')
EMAIL_DESTINATARIO_CC = os.getenv('DESTINATARIO_CC')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
EMAIL_ASUNTO = os.getenv('ASUNTO')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('Index.html')

def send_async_email(app, msg, remitente, destinatarios, password):
    with app.app_context():
        try:
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            if EMAIL_USE_TLS:
                server.starttls()
            server.login(remitente, password)
            server.sendmail(remitente, destinatarios, msg.as_string())
            server.quit()
        except Exception as e:
            print(f"Error al enviar el correo: {str(e)}")

@app.route('/send_email', methods=['POST'])
def send_email():
    nombre = request.form.get('nombre')
    empresa = request.form.get('empresa')
    cargo = request.form.get('cargo')
    email = request.form.get('email')
    telefono = request.form.get('telefono')
    mensaje = request.form.get('mensaje')

    # chequea que existan todos los campos del formulario que son obligatorios
    if not all([nombre, email, telefono, mensaje]):
        return jsonify({"message": "Campos Obligatorios no ingresados."}), 400

    # SMTP configuracion del servidor
    remitente = EMAIL_HOST_USER
    password = EMAIL_HOST_PASSWORD
    destinatario = EMAIL_DESTINATARIO
    destinatario_cc = EMAIL_DESTINATARIO_CC  # Puede ser opcional
    asunto = EMAIL_ASUNTO

    # chequea que exista la configuración del servidor SMTP
    if not remitente or not password:
        return jsonify({"message": "Error en la configuración del servidor SMTP."}), 500

    # Gererar el cuerpo del mensaje
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    if destinatario_cc:
        msg['Cc'] = destinatario_cc  
    msg['Subject'] = asunto

    body = f"""
    Nombre: {nombre}
    Empresa: {empresa}
    Cargo: {cargo}
    Email: {email}
    Teléfono: {telefono}
    Mensaje: {mensaje}
    """
    msg.attach(MIMEText(body, 'plain'))

    # Crear lista de destinatarios sin duplicados
    destinatarios = list(set([destinatario] + ([destinatario_cc] if destinatario_cc else [])))

    # Enviar el correo de manera asíncrona
    Thread(target=send_async_email, args=(app, msg, remitente, destinatarios, password)).start()
    return jsonify({"message": "Gracias por ponerse en contacto con Tradicom S.A. nos comunicaremos con ud. a la brevedad"}), 200

if __name__ == '__main__':
    app.run(debug=True)