from scrap_pb2_grpc import ScrapearPaginasServicer
import grpc
from concurrent import futures
import scrap_pb2
import sys
import scrap_pb2_grpc
import json
# Iportamos para el clickhouse
import clickhouse_connect
# Añadimos la ruta a los scrapers
sys.path.append('../')
# Importamos los scrapers
from cdruni import DruniScraper
from cpccomponentes import PccomponentesScraper
# Conectamos a la base de datos ingresando las credenciales de acceso a ella
if __name__ == '__main__':
    client = clickhouse_connect.get_client(
        host='boe4x1d321.eu-west-1.aws.clickhouse.cloud',
        user='default',
        password='wuFEakMj3Hp5_',
        secure=True
    )
class ServicioScrapear(ScrapearPaginasServicer):
    def ScrapearPagina(self, request, context):
        # Definimos url
        url = request.url
        # Miramos si es uno de los urls que soportamos
        if "druni" in url:
            # Borramos los tabla si existe
            client.command('DROP TABLE IF EXISTS druni')
            # Creamos la tabla de druni donde vamos a guardar los datos 
            client.command('CREATE TABLE druni (sku Int32, name String,image String, href String, pvp_price Int32, old_price Int32, stock Bool ) ENGINE MergeTree ORDER BY sku')
            # Instanciamos DruniScraper
            scraper = DruniScraper()  
            # Ejecuta el scraper de Druni
            scrap_datos = scraper.scrap_druni()  
            #print(scrap_datos)
            try:
                # Hacemos un bucle donde lo recorrer la lista de los productos que hemos guardado para almacenarlos en la base de datos
                for producto in scrap_datos:
                        fila = (
                            producto["sku"],
                            producto["name"],
                            producto["url"],
                            producto["image"],
                            producto["pvp_price"],
                            producto["old_price"],
                            producto["stock"]
                        )
                        # Variable para almacenar los datos de que seleccionamos
                        datos = [fila] 
                        #Datos almacenados 
                        # Insertamos los datos en la tabla
                        client.insert('druni', datos)
                print(f"Se guardaron {len(scrap_datos)} productos en la BD Druni")
            except Exception as e:
                    print(f"Error Excepcion {e} a la hora de estar añadiendo los datos a la base de datos")
                # Devolvemos los datos extraidos en formato JSON
            return scrap_pb2.ScrapearRespuesta(datos=json.dumps(scrap_datos))
        elif "pccomponentes" in url:
            # Borramos la tabla si existe
            client.command('DROP TABLE IF EXISTS pccomponentes')
            # Creamos la tabla de pccomponentes donde vamos a guardar los datos
            client.command('CREATE TABLE pccomponentes (sku Int32, name String, image String, href String, pvp_price Int32, old_price Int32, stock Bool ) ENGINE MergeTree ORDER BY sku')
            scraper = PccomponentesScraper()
            # Ejecuta el scraper de PcComponentes
            scrap_datos = scraper.scrap_pc_componentes()
            try:
                # Hacemos un bucle donde lo recorrer la lista de los productos que hemos guardado para almacenarlos en la base de datos
                for producto in scrap_datos:
                        fila = (
                            producto["sku"],
                            producto["name"],
                            producto["url"],
                            producto["image"],
                            producto["pvp_price"],
                            producto["old_price"],
                            producto["stock"]
                        )
                        # Variable para almacenar los datos de que seleccionamos
                        datos = [fila] 
                        # Insertamos los datos en la tabla
                        client.insert('pccomponentes', datos)
                print(f"Se guardaron {len(scrap_datos)} productos en la BD de Pccomponentes")
            except Exception as e:
                    print(f"Error Excepcion {e} a la hora de estar añadiendo los datos a la base de datos")
            return scrap_pb2.ScrapearRespuesta(datos=json.dumps(scrap_datos))
        else:
            return scrap_pb2.ScrapearRespuesta(datos="URL no soportada")
def serve():
    # Indicamos cuantos hilos manejamos a la vez "clientes"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    # Añadimos el servicio al servidor
    scrap_pb2_grpc.add_ScrapearPaginasServicer_to_server(ServicioScrapear(), server)  
    # Indicamos el puerto en el que queremos escuchar las peticiones
    server.add_insecure_port('[::]:50051')
    # Iniciamos el servidor
    print("El servidor se está ejecutando correctamente")
    server.start()
    # Mantenemos el servidor en ejecución
    print("Servidor GRPC escuchando en el puerto 50051")
    server.wait_for_termination()
# Si ejecutamos directamente este archivo se ejecutara la funcion de serve()
if __name__ == "__main__":  
    serve()
