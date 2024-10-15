# SANTIAGO RODRIGUEZ TOCA
# 14-10-2024
# Importamos las librerias que vamos a utilizar
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
#Clase DruniScraper
class DruniScraper:
    # Constructor de la clase
    def __init__(self, nombre_json="datos_druni.json", tipo_categoria="perfumes/hombre", paginas=1):
        self.nombre_json = nombre_json
        self.tipo_categoria = tipo_categoria
        self.paginas = paginas
    # Recogemos la url mediante esta función
    def urls_druni(self, categoria, paginas):
        # Almacenamos la URL general de DRUNI.ES
        url_general = "https://www.druni.es/"
        # Variable para unir la url general con la categoría que se elija
        urls_contenido = [url_general + categoria]
        # Miramos si hay valor en páginas
        if paginas is not None:
            # Recorremos las páginas desde la número 1 hasta las páginas que hemos pasado en la variable (paginas)
            paginas_salvadas = paginas + 1
            # Hacemos el bucle para recorrer
            for pagina in range(2, paginas_salvadas):
                # Añadimos el (?p=) para movernos a través de todas las páginas
                urls_contenido.append(f"{url_general}{categoria}?p={pagina}")
        # Devolvemos la lista de urls las cuales vamos a sacar la información
        return urls_contenido
    # Función para obtener la información de las páginas
    def obtener_datos(self, driver, url):
        # Hacemos la solicitud GET a la página
        driver.get(url)
        sleep(0.3)
        productos = []
        # Buscamos en el navegador los elementos que tipo div que tengan esta clase
        elementos_productos = driver.find_elements(By.XPATH, '//div[@class="products wrapper grid products-grid"]')
        # Si elementos_prodcutos tiene valor
        if elementos_productos:
            for elemento in elementos_productos[0].find_elements(By.XPATH, ".//li[contains(@class, 'item product product-item')]"):
                # Inicializamos las varaibles que vamos a usar
                sku = None
                titulo = None
                href = None
                imagen = None
                precio_venta = None
                precio_anterior = None
                descuento = None
                descripcion = None
                marca = None
                stock = True
            # =============================================================================================================================================
            # SKU del producto
                try: 
                    sku_producto = elemento.find_element(By.XPATH, './/div[@data-product-id]') 
                    sku = sku_producto.get_attribute('data-product-id') if sku_producto else None
                except Exception as e:
                    print(f"Error Excepcion: {e} en sku del producto")
            # =============================================================================================================================================
            # Titulo del producto
            #Hacemos la busqueda de titulos en los elementos (a) donde la clase sea la que indicamos en la busquedad (product-item-link)
                try: 
                    titulo_href_producto = elemento.find_element(By.XPATH,'.//a[@class="product-item-link"]')
                    titulo = titulo_href_producto.text.strip() if titulo_href_producto else None
                except Exception as e:
                    print(f"Error Excepcion: {e} en titulo del producto")
            # =============================================================================================================================================
            # HREF
                try:
                    href = titulo_href_producto.get_attribute('href') if titulo_href_producto else None
                except Exception as e:
                    print(f"Error Excepcion: {e} en href del producto")
            # =============================================================================================================================================
            #Imagen 
            # Hacemos la busqueda de imagenes en los elementos img y extraemos el valor de los atributos src
                try:
                    imagen_elemento = elemento.find_element(By.XPATH,".//img")
                    imagen = imagen_elemento.get_attribute('src') if imagen_elemento else None
                except Exception as e:
                    print(f"Error Excepcion: {e} en imagen del producto")
            # =============================================================================================================================================
            #Descripcion
            # Hacemos la busqueda de los elementos que sea de tipo div y que cuente con la clase (product description product-item-description)
                try:
                    elemento_descripcion = elemento.find_element(By.XPATH, ".//div[@class='product description product-item-description']")
                    descripcion = elemento_descripcion.text.strip()
                except Exception as e:
                    print(f"Error Excepcion: {e} en descripcion del producto")
            # =============================================================================================================================================
            # Marca
            # Hacemos la busqueda de las marcas en este caso estan almacenadas en la etiqueta p con clase (product-brand)
                try:
                    marca_elemento = elemento.find_element(By.XPATH, ".//p[@class='product-brand']")
                    marca = marca_elemento.text.strip()
                except Exception as e:
                    print(f"Error Excepcion: {e} en marca del producto")
            # =============================================================================================================================================
            # Disponibilidad
            # Hacemos un try debido a que si llega a faltar algun fallo se romperia el codigo y todos los datos que hemos recolectado hasta ese momento no se guardaran
                try:
                    estado_elemento = elemento.find_element(By.XPATH, ".//button[@class='action tocart']") 
                    stock = estado_elemento is not None
                    if stock:
                        #Precio venta
                        precio_venta_elemento = elemento.find_element(By.XPATH, ".//span[@data-price-type='finalPrice']")
                        # Establecemos el valor a la variable haciendo tambien un conversion a int
                        precio_venta = int(float(precio_venta_elemento.get_attribute('data-price-amount')) * 100) if precio_venta_elemento else None
                        #Precio anterior
                        precio_anterior_elemento = elemento.find_element(By.XPATH,".//span[@data-price-type='oldPrice']")
                        # Establecemos el valor a la variable haciendo tambien un conversion a int
                        precio_anterior = int(float(precio_anterior_elemento.get_attribute('data-price-amount')) * 100) if precio_anterior_elemento else None
                        #Descuento 
                        descuento_elemento = elemento.find_element(By.XPATH, ".//div[@class='discount-box']")
                        # Converitmos a entero el anterior valor de (descuento) y remplazamos lo que no necesitamos
                        descuento = int(descuento_elemento.text.replace("-","").replace("%","").strip()) if descuento_elemento else 0
                except Exception:# Si la excepcion salta quiere decir que los productos no tienen el boton de (añadir al carrito) lo cual nos indicara que no esta en stock
                    stock = None
            # =============================================================================================================================================
            # Añadimos el SKU a la lista de productos
                if sku is not None:
                    producto = {
                        "sku": sku,
                        "titulo": titulo,
                        "url": href,
                        "image": imagen,
                        "description": descripcion,
                        "marca": marca,
                        "pvp_price": precio_venta,
                        "old_price": precio_anterior,
                        "discount_percent": descuento,
                        "stock": stock
                    }
                # Añadimos el producto nuevo al diccionario
                    productos.append(producto)
                else:
                # Si el sku es None, mostramos un error por pantalla el cual nos indica que no se ha agregado un producto
                    print("No se ha agregado producto nuevo")
        else:
            # Si del find_all no se encontro nada mostramos el error de que no se encontro productos
            print("No se encontraron productos")
            # Retornamos los productos que hemos almacenado
        return productos
    # Función para hacer el scraper de la tienda
    def scrap_druni(self):
        # Lista para resultados
        resultados = []
        # Variable para almacenar las url con categoria y paginas en total de la categoria 
        totalUrls = self.urls_druni(self.tipo_categoria, self.paginas)
        opciones = Options()
        # Colocamos el user agent para indicar el navegador que estamos utilizando
        opciones.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chome/113.0.0.0 Safari/537.36")
        # Iniciamos este seudo navegador
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opciones)
        
        for url in totalUrls:
            productos = self.obtener_datos(driver, url)
            resultados.extend(productos)
        # Imprimimos por consola el número de resultados que obtuvimos
        print(f"Se obtuvieron {len(resultados)} productos en total")
        # Guardamos los datos en "JSON"
        with open(self.nombre_json, "w", encoding="utf-8") as file:
            json.dump(resultados, file, ensure_ascii=False, indent=4)
        print(f"Se guardaron {len(resultados)} artículos en " + self.nombre_json)
        # Cerramos el navegador al finalizar
        driver.quit()
        return resultados
