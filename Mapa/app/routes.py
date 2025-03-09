# import base64
# import io
# import logging
# import os
# from flask import Blueprint, json, request, jsonify, send_file
# import datetime
# import ee
# import requests
# from .ee_utils import image_to_map_id
# from shapely.geometry import shape
# import geotiff
# from bs4 import BeautifulSoup
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from .models.database import db
# main_routes = Blueprint('main_routes', __name__)



# @main_routes.before_app_request
# def before_request():
#     ee.Initialize()


# @main_routes.route('/')
# def hello_world():
#     return 'Hello World!'

# @main_routes.route("/ping")
# def ping_db():
#     try:
#         db.engine.execute("SELECT 1")
#         return jsonify({"message": "✅ Base de datos conectada correctamente"}), 200
#     except Exception as e:
#         return jsonify({"error": f"❌ No se pudo conectar a la base de datos: {e}"}), 500


# @main_routes.route('/coords', methods=['POST'])
# def process_coordinates():
#     data = request.get_json()
#     coordinates = data.get('coordinates', [])

#     polygon = ee.Geometry.Polygon(coordinates)
#     image = ee.ImageCollection('ECMWF/ERA5_LAND/HOURLY').first()
#     image_clipped = image.clip(polygon)

#     vis_params = {
#         'bands': ['temperature_2m'],
#         'min': 250,
#         'max': 320,
#         'palette': [
#             '000080', '0000d9', '4000ff', '8000ff', '0080ff', '00ffff',
#             '00ff80', '80ff00', 'daff00', 'ffff00', 'fff500', 'ffda00',
#             'ffb000', 'ffa400', 'ff4f00', 'ff2500', 'ff0a00', 'ff00ff',
#         ]
#     }

#     url_data = image_to_map_id(image_clipped, vis_params)
#     if 'errMsg' in url_data:
#         return jsonify({"error": url_data['errMsg']}), 500
#     return jsonify({"url": url_data['url']}), 200

# @main_routes.route('/precipitation', methods=['POST'])
# def process_precipitation():
#     data = request.get_json()
#     coordinates = data.get('coordinates', [])

#     end_date = datetime.datetime.utcnow()
#     start_date = end_date - datetime.timedelta(days=1)

#     start_date_str = start_date.strftime('%Y-%m-%d')
#     end_date_str = end_date.strftime('%Y-%m-%d')

#     polygon = ee.Geometry.Polygon(coordinates)
#     collection = ee.ImageCollection('NASA/GPM_L3/IMERG_V06')\
#         .select('precipitationCal')\
#         .filterDate(start_date_str, end_date_str)\
#         .filterBounds(polygon)

#     daily_precipitation = collection.reduce(ee.Reducer.sum()).rename('daily_total_precipitation')
#     daily_precipitation_clipped = daily_precipitation.clip(polygon)

#     vis_params = {
#         'bands': ['daily_total_precipitation'],
#         'min': 0,
#         'max': 50,
#         'palette': [
#             '000080', '0000d9', '4000ff', '8000ff', '0080ff', '00ffff',
#             '00ff80', '80ff00', 'daff00', 'ffff00', 'fff500', 'ffda00',
#             'ffb000', 'ffa400', 'ff4f00', 'ff2500', 'ff0a00', 'ff00ff',
#         ]
#     }

#     url_data = image_to_map_id(daily_precipitation_clipped, vis_params)
#     if 'errMsg' in url_data:
#         return jsonify({"error": url_data['errMsg']}), 500
#     return jsonify({"url": url_data['url']}), 200

# @main_routes.route('/prueba', methods=['POST'])
# def process_geojson():
#     try:
#         data = request.get_json()
#         coordinates = data.get('coordinates', [])

#         geojson_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'colombia.geo.json')
#         with open(geojson_path, 'r') as file:
#             geojson_data = json.load(file)

#         polygon = shape({
#             "type": "Polygon",
#             "coordinates": [coordinates]
#         })

#         features_within_polygon = []
#         for feature in geojson_data['features']:
#             feature_shape = shape(feature['geometry'])
#             if polygon.contains(feature_shape) or polygon.intersects(feature_shape):
#                 features_within_polygon.append(feature)

#         filtered_geojson = {
#             "type": "FeatureCollection",
#             "features": features_within_polygon
#         }

#         return jsonify(filtered_geojson)

#     except FileNotFoundError:
#         return jsonify({"error": "Archivo GeoJSON no encontrado"}), 404

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @main_routes.route('/<string:filename>', methods=['GET'])
# def get_geojson(filename):
#     files_mapping = {
#         'process_geojson': 'resguardos.geojson',
#         'lim_geojson': 'LimiteDep.geojson',
#         'res_geojson': 'Mparticipación.geojson'
#     }

#     geojson_filename = files_mapping.get(filename)

#     if not geojson_filename:
#         return jsonify({"error": "Ruta de archivo GeoJSON no válida"}), 400

#     return serve_geojson_file(geojson_filename)

# def serve_geojson_file(geojson_filename):
#     try:
#         geojson_path = os.path.join(os.path.dirname(__file__), '..', 'static', geojson_filename)

#         with open(geojson_path, 'r', encoding='utf-8') as file:
#             geojson_data = json.load(file)
        
#         response = jsonify(geojson_data)
#         response.headers['Content-Type'] = 'application/json; charset=utf-8'
#         return response

#     except FileNotFoundError:
#         return jsonify({"error": "Archivo GeoJSON no encontrado"}), 404

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @main_routes.route('/timeSeriesIndex', methods=['POST'])
# def time_series_index():
#     try:
#         logging.info("Received a request to /timeSeriesIndex")

#         data = request.get_json()
#         coordinates = data.get('coordinates', [])
#         date_from = data.get('dateFrom', '2020-01-01')
#         date_to = data.get('dateTo', '2021-12-31')
#         index_name = data.get('indexName', 'NDVI')

#         geometry = ee.Geometry.Polygon(coordinates)
#         collection = ee.ImageCollection('MODIS/006/MOD13A1').filterDate(date_from, date_to).filterBounds(geometry)

#         def calculate_index(image):
#             return image.normalizedDifference(['sur_refl_b02', 'sur_refl_b01']).rename(index_name)

#         indexed_collection = collection.map(calculate_index)

#         def reduce_image(image):
#             reduction = image.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=500)
#             return ee.Feature(None, {'value': reduction.get(index_name)})

#         time_series_features = indexed_collection.map(reduce_image).getInfo()['features']

#         formatted_time_series = []
#         for feature in time_series_features:
#             date_str = feature['id']

#             try:
#                 date = datetime.datetime.strptime(date_str, '%Y_%m_%d').strftime('%Y-%m-%d')
#             except ValueError as e:
#                 print(f"Error parsing date from feature ID '{date_str}': {e}")
#                 continue

#             value = feature['properties']['value']
#             formatted_time_series.append({'date': date, 'value': value})

#         return jsonify({"timeSeries": formatted_time_series}), 200
#     except Exception as e:
#         logging.error(f"Error processing the request: {e}", exc_info=True)
#         return jsonify({"error": str(e)}), 500


# @main_routes.route('/geojson-from-url', methods=['POST'])
# def geojson_from_url():
#     try:
#         data = request.get_json()
#         url = data.get('url')
#         response = requests.get(url)
        
#         if response.status_code != 200:
#             return jsonify({"error": "No se pudo descargar el archivo GeoJSON"}), 500

#         geojson_data = response.json()

#         return jsonify(geojson_data)

#     except Exception as e:
#         logging.error(f"Error processing GeoJSON from URL: {e}")
#         return jsonify({"error": str(e)}), 500

# with open('credentials.json') as f:
#     credentials_info = json.load(f)
# credentials = service_account.Credentials.from_service_account_info(credentials_info)
# drive_service = build('drive', 'v3', credentials=credentials)

# @main_routes.route('/download-tiff', methods=['GET'])
# def download_tiff():
#     try:
#         file_id = "1pDVoSLiq3jWConUmFnbhkLE6ZCYrpNy3"
#         request = drive_service.files().get_media(fileId=file_id)
#         response = request.execute()

#         return send_file(io.BytesIO(response), mimetype='image/tiff')
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
