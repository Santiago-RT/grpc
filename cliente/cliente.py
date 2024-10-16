import grpc
import sys
# Importamos las rutas de donde tenemos el servidor y los scrpaer
sys.path.append('../')
sys.path.append('../servidor')
import scrap_pb2 
import scrap_pb2_grpc

def iniciar(url):
    # Conectamos el cliente con el servidor en el puerto que indicamos el servidor
    with grpc.insecure_channel("localhost:50051") as channel:
        # Creamos el stub 
        stub = scrap_pb2_grpc.ScrapearPaginasStub(channel)
        # Enviamos solicitud de scraping con la URL que colocamos
        response = stub.ScrapearPagina(scrap_pb2.ScrapearPeticion(url=url))
        # Imprimimos los datos obtenidos
        #print(response.datos)
# Cuando ejecutemos directamente este archivo se inciara la funcion de inciar(url) ade más de crear la el bucle while True para preguntar al usuario hasta que deje de scrapear paginas
if __name__ == '__main__':
    while True:
        #Mensaje para indicar las paginas que se pueden hacer scraper
        print("Programa para hacer scraper")
        print("Paginas disponibles para hacer scrap: Druni y Pccomponentes")
        # Permitir que el usuario introduzca la URL
        url_a_scrapear = input("Introduce la URL a scrapear: ")
        iniciar(url_a_scrapear)
        
        # Preguntamos si desea continuar haciendo scraper en las paginas, quitando los espacios en blanco y siempre convirtiendo el texto a minusculas
        continuar = input("¿Quieres scrapear otra página? (sí/no): ").strip().lower()
        # si el usuario no coloco algo diferente a "si"
        if continuar != 'si':
            print("Adios")
            break
