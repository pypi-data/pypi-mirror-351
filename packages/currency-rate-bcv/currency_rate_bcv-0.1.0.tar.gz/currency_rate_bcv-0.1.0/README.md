# currency_rate_bcv

Librería en Python para obtener la tasa oficial del Euro y Dólar publicada por el Banco Central de Venezuela (BCV).

## Descripción

`currency_rate_bcv` permite consultar de forma sencilla y programática el valor actual del Euro y el Dólar según la tasa oficial publicada en la página del BCV. Ideal para proyectos financieros, aplicaciones de conversión de divisas o cualquier sistema que requiera la tasa oficial venezolana.

## Instalación

Puedes instalar la librería usando pip:

```sh
pip install currency_rate_bcv
```

O bien, clona el repositorio y usa:

```sh
pip install .
```

## Requisitos

- Python >= 3.6
- requests
- beautifulsoup4

## Uso

```python
import asyncio
from currency_rate_bcv.currency import Currency

async def main():
    currency = Currency()
    euro = await currency.getEuro
    print(f"Tasa oficial del Euro: {euro}")
    dollar = await currency.getDollar
    print(f"Tasa oficial del Dólar: {dollar}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Métodos

- `getEuro`: Devuelve la tasa oficial del Euro.
- `getDollar`: Devuelve la tasa oficial del Dólar.

Ambos métodos son propiedades asíncronas.

## Licencia

MIT

## Autor

Jarvis Gabriel Huice Padron  
[jarvis.realg@gmail.com](mailto:jarvis.realg@gmail.com)
