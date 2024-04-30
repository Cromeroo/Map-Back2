from flask import Blueprint, request, jsonify
import requests

weather_api = Blueprint('weather_api', __name__)

API_KEY = "0986e36c853a86df0015b80864aa0904"

@weather_api.route('/clima', methods=['GET'])
def obtener_clima():
    latitud = request.args.get('lat')
    longitud = request.args.get('lon')
    if not latitud or not longitud:
        return jsonify({'error': 'Faltan parámetros necesarios: latitud y longitud'}), 400
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitud}&lon={longitud}&appid={API_KEY}&units=metric&lang=es"
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        datos_clima = respuesta.json()
        return jsonify(datos_clima)
    else:
        return jsonify({'error': 'No se pudo obtener los datos del clima'}), respuesta.status_code
    
@weather_api.route('/prueba', methods=['GET'])
def hello_world():
    return 'Hello World!'
