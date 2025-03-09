# import ee
# import sys


# def image_to_map_id(ee_image, vis_params={}):
#     """  """
#     try:
#         map_info = ee_image.getMapId(vis_params)
#         return {
#             'url': map_info['tile_fetcher'].url_format
#         }
#     except Exception as e:
#         print("Error in image_to_map_id:", e)
#         return {
#             'errMsg': str(e)
#         }


# def get_time_series_by_collection_and_index(collection_name, index_name, scale, coords=[], date_from=None, date_to=None,
#                                             reducer=None):
#     """  """
#     try:
#         geometry = None
#         if isinstance(coords[0], list):
#             geometry = ee.Geometry.Polygon(coords)
#         else:
#             geometry = ee.Geometry.Point(coords)
#         if index_name:
#             index_collection = ee.ImageCollection(collection_name).filterDate(date_from, date_to).select(index_name)
#         else:
#             index_collection = ee.ImageCollection(collection_name).filterDate(date_from, date_to)

#         def get_index(image):
#             """  """
#             if reducer:
#                 the_reducer = eval("ee.Reducer." + reducer + "()")
#             else:
#                 the_reducer = ee.Reducer.mean()
#             if index_name:
#                 index_value = image.clip(geometry).reduceRegion(the_reducer, geometry, scale, maxPixels=1.0E13).get(index_name)
#             else:
#                 index_value = image.reduceRegion(the_reducer, geometry, scale, maxPixels=1.0E13)
#             return ee.Image().set('indexValue', [ee.Number(image.get('system:time_start')), index_value])

#         return {
#             'timeseries': index_collection.map(get_index).aggregate_array('indexValue').getInfo()
#         }
#     except Exception as e:
#         print(str(e))
#         raise Exception(sys.exc_info()[0])

# def mask_s2_clouds(image):
#     """Masks clouds in a Sentinel-2 image using the QA band.

#     Args:
#         image (ee.Image): A Sentinel-2 image.

#     Returns:
#         ee.Image: A cloud-masked Sentinel-2 image.
#     """
#     # Seleccionar la banda de calidad (QA60) de la imagen.
#     qa = image.select('QA60')

#     # Los bits 10 y 11 de esta banda indican la presencia de nubes y cirro, respectivamente.
#     # Se crea una máscara para identificar estos bits.
#     cloud_bit_mask = 1 << 10  # Desplazar 1 a la izquierda 10 veces para crear una máscara para el bit de nubes.
#     cirrus_bit_mask = 1 << 11  # Desplazar 1 a la izquierda 11 veces para crear una máscara para el bit de cirro.

#     # La máscara se forma comprobando que ambos, el bit de nubes y el bit de cirro, sean 0 (indicando condiciones despejadas).
#     mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))

#     # La imagen se actualiza con esta máscara para excluir píxeles nublados y de cirro.
#     # Además, se divide por 10000 para convertir los valores a un rango de 0-1, que es común para las imágenes de reflectancia.
#     return image.updateMask(mask).divide(10000)


