# SANTIAGO RODRIGUEZ TOCA 
# 03 -10- 2024
# Importamos las librerias que vamos a necesitar para hacer el scraper de la pagina
from bs4 import BeautifulSoup
import cloudscraper
import json
class PccomponentesScraper:
    def __init__(self, nombreJSON="datos.json", tipo_categoria="tarjetas-graficas", paginas=1):
        self.nombreJSON = nombreJSON
        self.tipo_categoria = tipo_categoria
        self.paginas = paginas
    # Recoger mediante la funcion de urls_pc_componentes las URLS
    def urls_pc_componentes(self,categoria, paginas):
        # Hacemos una variable para almacenar la url general de PCCOMPONENTES
        url_general = "https://www.pccomponentes.com/"
        # Variable donde vamos almacenar la url principal y agregar la categoria
        urls_contenido = [url_general+ categoria]
        # Hacemos un if si las paginas estan establecidas, en caso de que esten establecidas aumentamos una para poder seguir avanzando de paginas
        if paginas is not None:
            # Recorremos las paginas desde la 1 hasta el numero de paginas que le pasamos en la varible "paginas"
            paginas_salvadas = paginas+1
        # Hacemos un bucle for donde vamos a recorrer desde la pagina 2 ya que la primera pagina, ya se ejecutara cuando se haga la primera urls_contenido
        for pagina in range(2, paginas_salvadas):
            # Añadimos ?page= para movernos a traves de todas las paginas
            urls_contenido.append(f"{url_general}{categoria}?page={pagina}")
        # Devolvemos la lista de urls las cuales vamos a scrapear
        return urls_contenido
    # Obtener la información de la página
    def obtener_datos(self,url):
        # Header general para hacernos pasar como una persona real para hacer el scraper
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:85.0) Gecko/20100101 Firefox/85.0",
            'Accept': "*/*",
            'Accept-Language': "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            'DNT': "1",
            'Connection': "keep-alive",
            'Cache-Control': "max-age=0",
            'TE': "Trailers"
        }
        # Creamos una instancia de cloudscraper
        scraper = cloudscraper.create_scraper()
        # Hacemos la solicitud GET a la pagina colocando la url y la cabecera para la solicitud
        response = scraper.get(url, headers=headers)
        # Imprimimos el estado de la respuesta para verificar si fue correcta con (200)
        if response.status_code == 200:
            print(f"URL: {url}, Código de estado:{response.status_code}")
        else:
            # Si la respuesta de la peticion get no es correcta mostramos el codigo de estado y de color rojo
            print(f"URL: {url}, Código de estado:{response.status_code}")
        soup = BeautifulSoup(response.text, "html.parser")
        elementos_productos = soup.find("div", {"id": "category-list-product-grid"})
        productos = []
        if elementos_productos:
            for elemento in elementos_productos.find_all("a", {"data-testid": "normal-link"}):
                # Inicializamos variables
                sku = None
                titulo = None
                imagen = None
                precio_actual = None
                precio_anterior = None
                # =============================================================================================================================================
                # Sku del producto
                data_product_id = elemento.get("data-product-id")
                sku = data_product_id if data_product_id is not None else None
                # =============================================================================================================================================
                # Link del producto
                link_elemento = elemento.get("href") if elemento.get("href") else None
                # =============================================================================================================================================
                # Título
                h3 = elemento.find("h3", class_="product-card__title")
                titulo = h3.getText() if h3 else None
                # =============================================================================================================================================
                # Imagen
                imagen_elemento = elemento.find("img")
                imagen = imagen_elemento.get("src") if imagen_elemento else None
                # =============================================================================================================================================
                # Precios informacion
                # Encontrar el contenedor de precios
                informacion_precios = soup.find("div",class_="product-card__price-container")
                # =============================================================================================================================================
                # Precio actual
                # Buscamos la price card del producto
                precio_actual_span = elemento.find("span", {"data-e2e": "price-card"})
                # Miramos si precio_actual_span tiene algun valor, en caso de tener uno establecemos el valor a  una nueva variable precio_actual ademas luego obtenmos el texto de la busquedad y con (strip()) quitamos los espacios en blanco, ademas de que vamos a quitar el simbolos (€,) con replace(), si no le colocamos None
                if precio_actual_span:
                    # Obtenemos el texto del elemento, eliminando el símbolo de euro y procesando el formato
                    precio_actual = precio_actual_span.text.strip().replace(".","").replace("€","").replace(",",".") 
                    #print(f"Precio actual : {precio_actual}")
                # =============================================================================================================================================
                # Buscamos el precio anterior si hay 
                precio_anterior_span = informacion_precios.find("span", {"data-e2e": "crossedPrice"})
                # Hacemos un if para mirar si precio_anterior_span tiene valor , almacenamos el valor a la variable precio_antetior
                if precio_anterior_span :
                    # Obtenemos el texto del elemento, eliminando el símbolo de euro y procesando el formato
                    precio_anterior = precio_anterior_span.text.strip().replace(".","").replace("€","").replace(",",".")
                # =============================================================================================================================================
                if sku is not None:  # Si el sku está definido, vamos añadiendo los valores al producto 
                    producto = {
                        "sku": sku,
                        "url": link_elemento,
                        "name": titulo,
                        "image": imagen,
                        "pvp_price": int(float(precio_actual) *100)  if precio_actual else None,# Hacemos la conversion de la cadena decimal a entero
                        "old_price": int(float(precio_anterior) *100) if precio_anterior else None,# Hacemos la conversion de la cadena decimal a entero
                        "stock": True
                    }
                    # Añadimos el producto nuevo al diccionario
                    productos.append(producto)
                else: 
                    print("No se ha agregado el producto nuevo")
        else:
            print("No se encontraron productos.")
        
        return productos

    # Función para hacer el scraper de la tienda
    def scrap_pc_componentes(self):
        # Lista para resultados
        resultados = []
        # Variable para almacenar las url con categoria y paginas en total de la categoria
        totalUrls = self.urls_pc_componentes(self.tipo_categoria, self.paginas)
        # Hacemos un bule for in para recorrer el array url , luego a eso vamos extendiendo los resultados para ir agregando al json
        for url in totalUrls:
            productos =self. obtener_datos(url)
            resultados.extend(productos)
        # Imprimimos por consola el numero de resultados que obtuvimos en la busquedad
        print(f"Se obtuvieron {len(resultados)} productos en total")
        # Guardamos los datos en "datos.json" y mostramos un mensaje por consola dando un mensaje de exito y que se guardaron los datos en el archivo
        with open(self.nombreJSON, "w", encoding="utf-8") as file:
            json.dump(resultados, file, ensure_ascii=False, indent=4)
        print(f"Se guardaron {len(resultados)} artículos en "+self.nombreJSON)
        return resultados