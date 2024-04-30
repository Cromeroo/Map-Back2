from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
from ee_utils import *
from flask_caching import Cache
import datetime
import logging
from flask import request, jsonify
import json
import os
from weather_api import weather_api  
from shapely.geometry import shape, Point
from ee_utils import mask_s2_clouds  # Asegúrate de que esta función esté definida en ee_utils o en el módulo correspondiente

import ee

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.register_blueprint(weather_api, url_prefix='/api')


@app.before_request
def before():
    ee.Initialize()


@app.route('/')
def hello_world():
    return 'Hello World!'

def maskS2clouds(image):
    qa = image.select('QA60')
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11
    mask = qa.bitwiseAnd(cloudBitMask).eq(0) \
        .And(qa.bitwiseAnd(cirrusBitMask).eq(0))
  
    return image.updateMask(mask).divide(10000)


def obtener_fecha_actual():
    today = datetime.date.today()
    fecha_actual = today.strftime("%Y-%m-%d")
    return fecha_actual


@app.route('/coords', methods=['POST'])
def process_coordinates():
    # Obtener las coordenadas del payload
    data = request.get_json()
    coordinates = data.get('coordinates', [])

    # Convertir las coordenadas en una geometría de Earth Engine
    polygon = ee.Geometry.Polygon(coordinates)

    # Cargar la colección de imágenes y seleccionar la primera imagen
    image = ee.ImageCollection('ECMWF/ERA5_LAND/HOURLY').first()

    # Recortar la imagen al polígono proporcionado
    image_clipped = image.clip(polygon)

    # Definir los parámetros de visualización (mismos que se usaban anteriormente)
    vis_params = {
        'bands': ['temperature_2m'],
        'min': 250,
        'max': 320,
        'palette': [
            '000080', '0000d9', '4000ff', '8000ff', '0080ff', '00ffff',
            '00ff80', '80ff00', 'daff00', 'ffff00', 'fff500', 'ffda00',
            'ffb000', 'ffa400', 'ff4f00', 'ff2500', 'ff0a00', 'ff00ff',
        ]
    }

    url_data = image_to_map_id(image_clipped, vis_params)
    if 'errMsg' in url_data:
        return jsonify({"error": url_data['errMsg']}), 500
    return jsonify({"url": url_data['url']}), 200


@app.route('/precipitation', methods=['POST'])
def process_precipitation():
    data = request.get_json()
    coordinates = data.get('coordinates', [])

    # Obtener la fecha actual en UTC y calcular el día anterior
    end_date = datetime.datetime.utcnow()  # Fecha actual en UTC
    start_date = end_date - datetime.timedelta(days=1)  # Un día antes de la fecha actual

    # Formatear las fechas para Google Earth Engine
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Convertir las coordenadas en una geometría de Earth Engine
    polygon = ee.Geometry.Polygon(coordinates)

    # Cargar la colección de imágenes y filtrar por las fechas establecidas
    collection = ee.ImageCollection('NASA/GPM_L3/IMERG_V06')\
        .select('precipitationCal')\
        .filterDate(start_date_str, end_date_str)\
        .filterBounds(polygon)

    # Sumar la precipitación diaria
    daily_precipitation = collection.reduce(ee.Reducer.sum()).rename('daily_total_precipitation')

    # Recortar la imagen de la suma diaria de precipitación al polígono proporcionado
    daily_precipitation_clipped = daily_precipitation.clip(polygon)

    # Definir los parámetros de visualización para la suma diaria de precipitación
    vis_params = {
        'bands': ['daily_total_precipitation'],
        'min': 0,
        'max': 50,  # Ajusta este valor según sea necesario, dependiendo de la precipitación esperada
        'palette': [
            '000080', '0000d9', '4000ff', '8000ff', '0080ff', '00ffff',
            '00ff80', '80ff00', 'daff00', 'ffff00', 'fff500', 'ffda00',
            'ffb000', 'ffa400', 'ff4f00', 'ff2500', 'ff0a00', 'ff00ff',
        ]
    }

    # Asume la existencia de una función image_to_map_id() que convierte una imagen de Earth Engine en una URL para visualización
    url_data = image_to_map_id(daily_precipitation_clipped, vis_params)
    if 'errMsg' in url_data:
        return jsonify({"error": url_data['errMsg']}), 500
    return jsonify({"url": url_data['url']}), 200





@app.route('/prueba', methods=['POST'])
def process_geojson():
    try:
        data = request.get_json()
        coordinates = data.get('coordinates', [])

        # Cargar el archivo GeoJSON
        geojson_path = os.path.join(app.static_folder, 'colombia.geo.json')
        with open(geojson_path, 'r') as file:
            geojson_data = json.load(file)

        # Convertir las coordenadas en un objeto polígono de Shapely
        polygon = shape({
            "type": "Polygon",
            "coordinates": [coordinates]
        })

        # Filtrar las características del GeoJSON dentro del polígono
        features_within_polygon = []
        for feature in geojson_data['features']:
            feature_shape = shape(feature['geometry'])
            if polygon.contains(feature_shape) or polygon.intersects(feature_shape):
                features_within_polygon.append(feature)

        # Crear un nuevo objeto GeoJSON con las características filtradas
        filtered_geojson = {
            "type": "FeatureCollection",
            "features": features_within_polygon
        }

        return jsonify(filtered_geojson)

    except FileNotFoundError:
        return jsonify({"error": "Archivo GeoJSON no encontrado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/<string:filename>', methods=['GET'])
def proces_geojson(filename):
    # Diccionario que mapea los nombres de los endpoints a los nombres de archivos GeoJSON
    files_mapping = {
        'process_geojson': 'resguardos.geojson',
        'lim_geojson': 'LimiteDep.geojson',
        'res_geojson': 'Mparticipación.geojson'
    }

    # Obtener el nombre del archivo GeoJSON basado en el endpoint solicitado
    geojson_filename = files_mapping.get(filename)

    if not geojson_filename:
        return jsonify({"error": "Ruta de archivo GeoJSON no válida"}), 400

    return serve_geojson_file(geojson_filename)

def serve_geojson_file(geojson_filename):
    try:
        geojson_path = os.path.join(app.static_folder, geojson_filename)

        with open(geojson_path, 'r', encoding='utf-8') as file:
            geojson_data = json.load(file)
        
        response = jsonify(geojson_data)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

    except FileNotFoundError:
        return jsonify({"error": "Archivo GeoJSON no encontrado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500






@app.route('/timeSeriesIndex', methods=['POST'])
def time_series_index():
    try:
        logging.info("Received a request to /timeSeriesIndex")

        # Obtener los parámetros del payload
        data = request.get_json()
        coordinates = data.get('coordinates', [])
        date_from = data.get('dateFrom', '2020-01-01')  # Fecha de inicio (formato YYYY-MM-DD)
        date_to = data.get('dateTo', '2021-12-31')  # Fecha de fin (formato YYYY-MM-DD)
        index_name = data.get('indexName', 'NDVI')  # El índice que deseas calcular, por ejemplo NDVI

        # Convertir las coordenadas en una geometría de Earth Engine
        geometry = ee.Geometry.Polygon(coordinates)

        # Definir la colección de imágenes y filtrar por fecha y región
        collection = ee.ImageCollection('MODIS/006/MOD13A1').filterDate(date_from, date_to).filterBounds(geometry)

        # Calcular el índice para cada imagen, si es necesario
        def calculate_index(image):
            return image.normalizedDifference(['sur_refl_b02', 'sur_refl_b01']).rename(index_name)

        indexed_collection = collection.map(calculate_index)

        # Aplicar un reductor para obtener la serie temporal del índice
        def reduce_image(image):
            reduction = image.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=500)
            return ee.Feature(None, {'value': reduction.get(index_name)})

        # Mapear reduce_image sobre la colección
        time_series_features = indexed_collection.map(reduce_image)

        # Obtener los resultados con getInfo()
        time_series_list = time_series_features.getInfo()['features']

        # Formatear las fechas y preparar los datos para el cliente web
        formatted_time_series = []
        for feature in time_series_list:
            # Extraer el ID del feature, que parece contener la fecha
            date_str = feature['id']

            # Convertir la cadena de fecha del ID a un formato de fecha legible
            # Asumiendo que el formato es 'YYYY_MM_DD'
            try:
                date = datetime.datetime.strptime(date_str, '%Y_%m_%d').strftime('%Y-%m-%d')
            except ValueError as e:
                print(f"Error parsing date from feature ID '{date_str}': {e}")
                continue  # Saltar este feature si la fecha no se puede parsear

            # Obtener el valor asociado con este feature
            value = feature['properties']['value']

            # Agregar la fecha formateada y el valor a la lista
            formatted_time_series.append({'date': date, 'value': value})

        # Devolver los resultados formateados
        return jsonify({"timeSeries": formatted_time_series}), 200
    except Exception as e:
        logging.error(f"Error processing the request: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500









if __name__ == "_main_":
    app.run(port = 5000, debug = True)