from flask import Flask, request
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

app = Flask(__name__)

# Credenciales Meta
META_PHONE_NUMBER_ID = os.getenv('META_PHONE_NUMBER_ID')
META_BUSINESS_ACCOUNT_ID = os.getenv('META_BUSINESS_ACCOUNT_ID')
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN', 'tu_token_secreto')

# Base de datos simple
citas = {}

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verifica que el webhook es válido"""
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if token == WEBHOOK_VERIFY_TOKEN:
        return challenge
    return 'Invalid token', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recibe mensajes de WhatsApp"""
    try:
        body = request.get_json()
        
        # Extrae mensaje
        if body['entry'][0]['changes'][0]['value'].get('messages'):
            message = body['entry'][0]['changes'][0]['value']['messages'][0]
            from_number = message['from']
            incoming_msg = message['text']['body'].lower()
            
            print(f"Mensaje de {from_number}: {incoming_msg}")
            
            # Lógica del bot
            if incoming_msg == 'hola':
                respuesta = "¡Hola! Escribe 'agendar' para reservar una cita."
            elif incoming_msg.startswith('agendar'):
                respuesta = "¿Qué día y hora quieres tu cita? (ej: lunes 15:00)"
                citas[from_number] = {'estado': 'esperando_hora'}
            elif from_number in citas and citas[from_number].get('estado') == 'esperando_hora':
                citas[from_number]['hora'] = incoming_msg
                respuesta = f"✅ Cita agendada para {incoming_msg}."
                citas[from_number]['estado'] = 'confirmada'
            else:
                respuesta = "No entiendo. Escribe 'hola' para empezar."
            
            # Envía respuesta
            send_message(from_number, respuesta)
        
        return 'OK', 200
    except Exception as e:
        print(f"Error: {e}")
        return 'OK', 200

def send_message(to_number, message_text):
    """Envía mensaje por WhatsApp"""
    url = f"https://graph.instagram.com/v18.0/{META_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
