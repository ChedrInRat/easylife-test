import db
from db import TransactionModel, UserModel, TransactionType, CreateUserModel, CreateTransactionModel
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse



app = FastAPI()
templates = Jinja2Templates(directory='templates')


@app.post('/user')
async def add_user(user:CreateUserModel) -> int|None:
    return db.add_user(user.name)
    

@app.get('/user')
async def get_all_user(limit:int = 50, page:int = 1) -> list[UserModel]|None:
    return db.get_all_user(limit=limit, page=page)
     

@app.get('/user/{user_id}')
async def get_user(user_id:int) -> UserModel|None:
    return db.get_user(user_id=user_id)


@app.patch('/user/{user_id}')
async def upd_user(user_id:int, user:CreateUserModel):
    db.upd_user(user_id, user)


@app.delete('/user/{user_id}')
async def del_user(user_id:int):
    db.del_user(user_id)
    return {"message": "User deleted"}


@app.post('/transaction')
async def add_transactions(transaction:CreateTransactionModel) -> int|None:
    return db.add_transaction(transaction.user_id, transaction.t_type, transaction.amount)


@app.patch('/transaction/{transaction_id}')
async def upd_transaction(transaction_id:int, transaction:CreateTransactionModel):
    print(transaction_id, transaction)
    db.upd_transaction(transaction_id, transaction)


@app.delete('/transaction/{transaction_id}')
async def del_transaction(transaction_id:int):
    db.del_transaction(transaction_id)
    return {"message": "Transaction deleted"}


@app.get('/', response_class=HTMLResponse)
async def index():
    return templates.TemplateResponse("index.html") 


@app.get('/admin', response_class=HTMLResponse)
async def admin(request:Request):
    users = db.get_all_user() or []
    
    return templates.TemplateResponse("admin.html", {"request":request, "users":users}) 

@app.get('/user/{user_id}/stats')
async def user_stats(user_id:int, request:Request):
    user = db.get_user(user_id)
    stats = db.get_user_stat(user_id) 

    return templates.TemplateResponse("user_stats.html", {"request":request, "user":user, "stats":stats})
