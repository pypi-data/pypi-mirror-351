import asyncio
import requests
from bs4 import BeautifulSoup
import logging


class Currency:

    def __init__(self):
        self.__log = logging.getLogger(__name__)
        self.__log.info("inicio core tasa dollar")

    @property
    async def getEuro(self):

        url = "http://www.bcv.org.ve/"
        self.__log.info(
            "iniciando peticion al bcv para extraer el valor del euro   ")

        try:
            self.__log.info("entrando en la peticion")
            # Realizar la solicitud GET a la página del BCV
            respuesta = requests.get(url, verify=False)
            respuesta.raise_for_status()

            # Parsear el contenido HTML
            soup = BeautifulSoup(respuesta.content, 'html.parser')
            # self.__log.info(soup)
            # Buscar el elemento que contiene el precio del dólar
            elemento_dolar = soup.find('div', {'id': 'euro'})
            self.__log.info("verfificando respuesta del bcv")

            if elemento_dolar:

                self.__log.info("respuesta correcta del bcv")

                self.__log.info("recorriendo html del bcv")
                precio_dolar = elemento_dolar.text.strip()
                result = precio_dolar.replace(",", ".")
                det = result.replace('EUR  \n ', "").strip()
                det = det.replace(' ', "").strip()
                det = det.replace('EUR', "").strip()
                det = det.replace('U', "").strip()
                det = det.replace('R', "").strip()
                det = det.replace('\n', "").strip()
                self.__log.info(det)
                result = float(det)
                res = round(float(result), 2)
                self.__log.info("data extraida de manera correcta")

                self.__log.info(res)
                self.__log.info(type(res))
                return res
            else:
                self.__log.info("No se pudo encontrar el precio del dólar en la página del BCV.")

                return 0

        except requests.RequestException as e:
            self.__log.info(f"error al conectarse al bcv   {e}")
            return 0

    @property
    async def getDollar(self):

        url = "http://www.bcv.org.ve/"
        self.__log.info(
            "iniciando peticion al bcv para extraer el vlor del euro  ")

        try:
            self.__log.info("entrando en la peticion")
            # Realizar la solicitud GET a la página del BCV
            respuesta = requests.get(url, verify=False)
            respuesta.raise_for_status()

            # Parsear el contenido HTML
            soup = BeautifulSoup(respuesta.content, 'html.parser')
           
            # Buscar el elemento que contiene el precio del dólar
            elemento_dolar = soup.find('div', {'id': 'dolar'})
            self.__log.info("verfificando respuesta del bcv")
            
            if elemento_dolar:

                self.__log.info("respuesta correcta del bcv")

                self.__log.info("recorriendo html del bcv")
                precio_dolar = elemento_dolar.text.strip()
                self.__log.info(str(precio_dolar))
                result = precio_dolar.replace(",", ".")
                self.__log.info(str(result))
                det = result.replace('USD  \n ', "").strip()
                det = det.replace(' ', "").strip()
                det = det.replace('USD', "").strip()
                det = det.replace('S', "").strip()
                det = det.replace('D', "").strip()
                det = det.replace('\n', "").strip()
                self.__log.info(det)
                result = float(det)
                res = round(float(result), 2)
                self.__log.info("data extraida de manera correcta")

                self.__log.info(res)
                self.__log.info(type(res))
                return res
            else:
                self.__log.info("No se pudo encontrar el precio del dólar en la página del BCV.")

                return 0

        except requests.RequestException as e:
            self.__log.info(f"error al conectarse al bcv   {e}")
            return 0



async def main():
    euro = await  Currency().getEuro
    print("esta es la tasa " + str( euro))
    dollar =  await Currency().getDollar
    print("esta es la tasa d " + str(dollar))

if __name__ == '__main__':
    asyncio.run(main())
