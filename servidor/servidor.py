from scrap_pb2_grpc import ScrapearPaginasServicer
import grpc
from concurrent import futures
import scrap_pb2
import sys
import scrap_pb2_grpc
import json

# Añadimos la ruta a los scrapers
sys.path.append('../')

# Importamos los scrapers
from cdruni import DruniScraper
from cpccomponentes import PccomponentesScraper
class ServicioScrapear(ScrapearPaginasServicer):
    def ScrapearPagina(self, request, context):
        # Definimos url
        url = request.url
        # Miramos si es uno de los urls que soportamos
        if "druni" in url:
            # Instanciamos DruniScraper
            scraper = DruniScraper()  
            # Ejecuta el scraper de Druni
            scrap_datos = scraper.scrap_druni()  
            # Devolvemos los datos extraidos en formato JSON
            return scrap_pb2.ScrapearRespuesta(datos=json.dumps(scrap_datos))
        elif "pccomponentes" in url:
            scraper = PccomponentesScraper()
            # Ejecuta el scraper de PcComponentes
            scrap_datos = scraper.scrap_pc_componentes()
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
