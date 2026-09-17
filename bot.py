from flask import Flask, request
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

client = Client(ACCOUNT_SID, AUTH_TOKEN)

citas = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    
    if incoming_msg.lower() == 'hola':
        respuesta = "Hola! Escribe agendar"
    elif incoming_msg.lower().startswith('agendar'):
        respuesta = "Que hora quieres?"
        citas[from_number] = {'estado': 'esperando_hora'}
    elif from_number in citas and citas[from_number].get('estado') == 'esperando_hora':
        citas[from_number]['hora'] = incoming_msg
        respuesta = f"Cita agendada para {incoming_msg}"
    else:
        respuesta = "No entiendo"
    
    client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        body=respuesta,
        to=from_number
    )
    
    return 'OK', 200

if __name__ == '__main__':
    app.run()
