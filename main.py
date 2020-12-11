from db.user_db import UserInDB
from db.user_db import update_user, get_user

from db.transaction_db import TransactionInDB
from db.transaction_db import save_transaction

from models.user_models import UserIn, UserOut

from models.transaction_models import TransactionIn, TransactionOut

import datetime
from fastapi import FastAPI, HTTPException

api = FastAPI()

####################################################
from fastapi.middleware.cors import CORSMiddleware
origins = [     #Origenes desde donde se permitira entrar a la app
    "http://localhost.tiangolo.com", 
    "https://localhost.tiangolo.com",
    "http://localhost", 
    "http://localhost:8080",
    "https://cajero-front.herokuapp.com"
]
api.add_middleware(
    CORSMiddleware, allow_origins=origins,  #Agregar esos origenes al CORS
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
#####################################################

@api.post("/user/auth/")
async def auth_user(user_in: UserIn):#Recibe un usuario y contraseña
    user_in_db = get_user(user_in.username)#Verifica si el usuario existe
    if user_in_db == None:
        raise HTTPException(status_code=404, detail="El usuario no existe")
    if user_in_db.password != user_in.password:
        return {"Autenticado": False}
    return {"Autenticado": True}


@api.get("/user/balance/{username}")#Recibe el usuario en la url
async def get_balance(username: str):
    user_in_db = get_user(username)#Verifica si el usuario existe
    if user_in_db == None:
        raise HTTPException(status_code=404, detail="El usuario no existe")

    user_out = UserOut(**user_in_db.dict())#Mapea el usuario al UserOut
    return user_out


@api.put("/user/transaction/")
async def make_transaction(transaction_in: TransactionIn):#Recibe un usuario y valor a retirar
    user_in_db = get_user(transaction_in.username)#Verifica si el usuario existe

    if user_in_db == None:
        raise HTTPException(status_code=404, detail="El usuario no existe")

    if user_in_db.balance < transaction_in.value:
        raise HTTPException(status_code=400, detail="Sin fondos suficientes")

    user_in_db.balance = user_in_db.balance - transaction_in.value #Resta el balance actual con el valor que retiro
    update_user(user_in_db) #Actualiza el usuario

    transaction_in_db = TransactionInDB(
        **transaction_in.dict(), actual_balance=user_in_db.balance)
    transaction_in_db = save_transaction(transaction_in_db) #Guarda la transaccion

    transaction_out = TransactionOut(**transaction_in_db.dict()) #Pasa la transaccion para retornarla al usuario
    return transaction_out
