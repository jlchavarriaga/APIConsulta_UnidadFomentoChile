
from fastapi import FastAPI
from datetime import datetime
from bs4 import BeautifulSoup

import requests
import calendar
import locale
import re
import json

app = FastAPI()

encabezado ={
    "user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41"
}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/api/{date}')
def api(date: str):
    
    date_obj = datetime.strptime(date, '%d-%m-%Y')
    
    #Obtenemos el año de la fecha suministrada, para determinar que url debemos consultar 
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day
    
    # Establecemos la localización a español, para que el nombre del mes NO sea retornado en ingles
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    #Obtenemos el nombre del mes tomando el numero
    nameMonth=  calendar.month_name[month] 
    #nameMonth = datetime.strptime(str(month), "%m").strftime("%B")   #Opcion 2
    
    if date_obj: 
        #En el sitio web, si el año es anterior al 2012 entonces la consulta debe realizarse desde otro link
        if(year >=2013):
            url = 'https://www.sii.cl/valores_y_fechas/uf/uf'+year.__str__()+'.htm'
        else:
            url= f'https://www.sii.cl/pagina/valores/uf/uf{year}.htm'
            return {'error': 'Date not available (< 2013)'}
        
        #Capturamos la respuesta de la solicitud
        response = requests.get(url,headers=encabezado)

        if response.status_code == 200:
          # return response.json()
          # return response.text
       
            #Debemos recorrer la respuesta en busqueda del valor solicitado
            # ya sea por id (id='mes_mayo')  o por el nombre del mes con la etiqueta <h2>(Mayo)   
            
           idMont= f'mes_{nameMonth}'   #obtenemos el nombre del mes y generamos el id a buscar
           soup = BeautifulSoup(response.text)
                      
           contenedor=soup.find(id=idMont)   #buscamos la data con ese id asociado
           try:
            cadena = contenedor.text
           except:
               return {'error': 'Date not available'}

           valores = cadena.replace('\n', ' ').split()  #reemplazamos los saltos de linea por espacios en blanco
           
           diccionario = {}

            # recorremos los valores y comprobamos si el valor anterior si contiene un numero
           for i in range(1, len(valores)):
                if valores[i-1].isdigit():
                    diccionario[int(valores[i-1])] = valores[i]
           
           #return diccionario aca devolvemos todos los valores del mes 
           
           valor = diccionario[day]
           
           #return valor devolvermos solo el valor 
           
           # Creamos un diccionario con el valor del día
           resultado = {'dia': date.__str__(), 'valor': valor}
           
           # Convertimos el diccionario a formato JSON
           resultado_json = json.dumps(resultado)
           print (resultado_json)
           print (resultado)
           
           return resultado_json
           
    return {'error': 'Invalid date format'}
