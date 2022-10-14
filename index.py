from typing import Optional
from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, Request
from fastapi.responses  import RedirectResponse
from fastapi.responses import JSONResponse
from bins import mydict, get_bin_info
import re
from pydantic import BaseModel
from py_adyen_encrypt import encryptor
import urllib


def adyen_enc(cc, mes, ano, cvv, ADYEN_KEY, adyen_version):
    enc = encryptor(ADYEN_KEY)
    enc.adyen_version = adyen_version
    enc.adyen_public_key = ADYEN_KEY

    card = enc.encrypt_card(card=cc, cvv=cvv, month=mes, year=ano)
    month = card['month']
    year = card['year']
    cvv = card['cvv']
    card = card['card']

    card = urllib.parse.quote_plus(card)
    Month = urllib.parse.quote_plus(month)
    Year = urllib.parse.quote_plus(year)
    cvv = urllib.parse.quote_plus(cvv)
    return card, Month, Year,cvv


app = FastAPI(debug=True, 
              title="Bin lookup And Adyen Generator Ny Roldexverse.", 
              redoc_url=None,
              description=" Feel free to use. made by @roldexverse for roldexverse subscribers.")




class UnicornException(Exception):
    def __init__(self, name: str,  message: str):
        self.name = name
        self.message = message


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={'success': False, "message": exc.message},
    )


@app.get("/bin/{bin1}")
async def bin(bin1):
    price = bin1
    if not price.isdigit():
        raise HTTPException(
            status_code=404, detail="Give me 6 digits Numbers.")
    elif len(price) < 6:
        raise HTTPException(
            status_code=404, detail="Give me 6 numbers atleast.")
    bin = price[:6]
    bin_data = get_bin_info(bin)
    if not bin_data:
        raise HTTPException(status_code=404, detail="Bin Not Found")
    return {
        'bin': bin,
        'brand': bin_data['brand'],
        'type': bin_data['type'],
        'category': bin_data['category'],
        'issuer': bin_data['issuer'],
        'alpha_2': bin_data['alpha_2'],
        'alpha_3': bin_data['alpha_3'],
        'country': bin_data['country'],
        'bank_phone': bin_data['bank_phone'],
        'bank_url': bin_data['bank_url'],
        'prepaid': bin_data['prepaid'],                                                                               
    }


@app.get("/")
async def start():
    return RedirectResponse("http://www.github.com/lux404")


class Item(BaseModel):
    card: str
    month: str
    year: str
    cvv: str
    adyen_version: str
    adyen_key: str


@app.post("/adyen/")
async def adyen(item: Item):
    cc, mes, ano, cvv = adyen_enc(
        item.card, item.month, item.year, item.cvv, item.adyen_key, item.adyen_version)
    return {
        'card': cc,
        'month': mes,
        'year': ano,
        'cvv': cvv
    }
