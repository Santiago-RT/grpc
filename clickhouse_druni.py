# SANTIAGO RODRIGUEZ TOCA
# 07-10-2024
# Importamos las librerias que vamos a utilizar
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
# Iportamos para el clickhouse
import clickhouse_connect
if __name__ == '__main__':
    client = clickhouse_connect.get_client(
        host='boe4x1d321.eu-west-1.aws.clickhouse.cloud',
        user='default',
        password='wuFEakMj3Hp5_',
        secure=True
    )
# client = clickhouse_connect.get_client(host='https://boe4x1d321.eu-west-1.aws.clickhouse.cloud:8443', username='default', password='wuFEakMj3Hp5_')
# Borramos la tabla si existe
client.command('DROP TABLE IF EXISTS datos_druni')
# Creamos la tabla de druni donde vamos a guardar los datos en este caso el precio y el nombre
client.command('CREATE TABLE datos_druni (sku Int32, name String, pvp_price Int32, old_price Int32, stock Bool ) ENGINE MergeTree ORDER BY sku')
# Variables
# Nombre del archivo donde se van a guardar los datos
nombre_json = "datos_druni.json"
# Nombre de la categoría que vamos a usar
tipo_categoria = "perfumes/hombre"
# Número de páginas
paginas = 1
# Recogemos la url mediante esta función
def urls_druni(categoria, paginas):
    # Almacenamos la URL general de DRUNI.ES
    url_general = "https://www.druni.es/"
    # Variable para unir la url general con la categoría que se elija
    urls_contenido = [url_general + categoria]
    
    # Miramos si hay valor en páginas
    if paginas is not None:
        # Recorremos las páginas desde la número 1 hasta las páginas que hemos pasado en la variable (paginas)
        paginas_salvadas = paginas + 1
        # Hacemos el bucle para recorrer desde la página dos
        for pagina in range(2, paginas_salvadas):
            # Añadimos el (?p=) para movernos a través de todas las páginas
            urls_contenido.append(f"{url_general}{categoria}?p={pagina}")
    # Devolvemos la lista de urls las cuales vamos a sacar la información
    return urls_contenido
# Función para obtener la información de las páginas
def obtener_datos(driver, url):
    # Hacemos la solicitud GET a la página
    driver.get(url)
    # Esperamos un poco para que se cargue el contenido
    sleep(1) 
    productos = []
    # Buscamos en el navegador los elementos que tipo div que tengan esta clase
    elementos_productos = driver.find_elements(By.XPATH,'//div[@class="products wrapper grid products-grid"]')
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
                print(f"Errror Excepcion: {e} en sku del producto")
                sku= None
            # =============================================================================================================================================
            # Titulo del producto
            #Hacemos la busqueda de titulos en los elementos (a) donde la clase sea la que indicamos en la busquedad (product-item-link)
            try: 
                titulo_href_producto = elemento.find_element(By.XPATH,'.//a[@class="product-item-link"]')
                titulo = titulo_href_producto.text.strip() if titulo_href_producto else None
            except Exception as e:
                print(f"Errror Excepcion: {e} en titulo del producto")
                titulo= None
            
            # =============================================================================================================================================
            # HREF
            try:
                href = titulo_href_producto.get_attribute('href') if titulo_href_producto else None
            except Exception as e:
                print(f"Errror Excepcion: {e} en href del producto")
                href= None
            # =============================================================================================================================================
            #Imagen 
            # Hacemos la busqueda de imagenes en los elementos img y extraemos el valor de los atributos src
            try:
                imagen_elemento = elemento.find_element(By.XPATH,".//img")
                imagen = imagen_elemento.get_attribute('src') if imagen_elemento else None
            except Exception as e:
                print(f"Errror Excepcion: {e} en imagen del producto")
                imagen= None
            # =============================================================================================================================================
            #Descripcion
            # Hacemos la busqueda de los elementos que sea de tipo div y que cuente con la clase (product description product-item-description)
            try:
                elemento_descripcion = elemento.find_element(By.XPATH, ".//div[@class='product description product-item-description']")
                descripcion = elemento_descripcion.text.strip()
            except Exception as e:
                print(f"Errror Excepcion: {e} en descripcion del producto")
                descripcion= None
            # =============================================================================================================================================
            # Marca
            # Hacemos la busqueda de las marcas en este caso estan almacenadas en la etiqueta p con clase (product-brand)
            try:
                marca_elemento = elemento.find_element(By.XPATH, ".//p[@class='product-brand']")
                marca = marca_elemento.text.strip()
            except Exception as e:
                print(f"Errror Excepcion: {e} en marca del producto")
                marca= None
            # =============================================================================================================================================
            # Disponibilidad
            # Hacemos un try debido a que si llega a faltar algun fallo se romperia el codigo y todos los datos que hemos recolectado hasta ese momento no se guardaran
            try:
                estado_elemento = elemento.find_element(By.XPATH, ".//button[@class='action tocart']") 
                stock = estado_elemento
                if stock:
                        stock = True
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
                        if descuento_elemento:
                        # Converitmos a entero el anterior valor de (descuento) y remplazamos lo que no necesitamos
                            descuento = int(descuento_elemento.text.replace("-","").replace("%","").strip())
                        else :
                            0
            # Si la excepcion salta quiere decir que los productos no tienen el boton de (añadir al carrito) lo cual nos indicara que no esta en stock
            except Exception :
                stock = None
                
            # =============================================================================================================================================
            # Añadimos el SKU a la lista de productos
            if sku is not None:
                producto = {
                    "sku": sku,
                    "titulo":titulo,
                    "url":href,
                    "image":imagen,
                    "description": descripcion,
                    "marca": marca,
                    "pvp_price": precio_venta,
                    "old_price": precio_anterior,
                    "discount_percent":descuento,
                    "stock":stock
                }
                try:
                    # Variable donde vamos a indicar que vamos a guardar el la base de datos
                    fila = (sku, titulo, precio_venta, precio_anterior, stock)
                    # Variable para almacenar los datos de que seleccionamos
                    datos = [fila] 
                    #print(data)
                    # Insertamos los datos en la tabla
                    client.insert('datos_druni', datos)
                except Exception as e:
                    print(f"Error Excepcion {e} a la hora de estar añadiendo los datos a la base de datos")
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
def scrap_druni(categoria, paginas):
    # Lista para resultados
    resultados = []
    # Variable para almacenar las url con categoria y paginas en total de la categoria    
    totalUrls = urls_druni(categoria, paginas)
    opciones = Options()
    # Colocamos el user agent para indicar el navegador que estamos utilizando
    opciones.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chome/113.0.0.0 Safari/537.36")
    # Iniciamos este seudo navegador
    driver = webdriver.Chrome(
        # Descargamos el web driver necesario para selenium
        service=Service(ChromeDriverManager().install()),
        options = opciones
    )
    for url in totalUrls:  
        productos = obtener_datos(driver, url)
        resultados.extend(productos)
    # Imprimimos por consola el número de resultados que obtuvimos
    print(f"Se obtuvieron {len(resultados)} productos en total")
    
    # Guardamos los datos en "JSON"
    with open(nombre_json, "w", encoding="utf-8") as file:
        json.dump(resultados, file, ensure_ascii=False, indent=4)
    print(f"Se guardaron {len(resultados)} artículos en " + nombre_json)
    
    # Cerramos el navegador al finalizar
    driver.quit()
categoria = tipo_categoria
scrap_druni(categoria, paginas)

