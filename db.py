import sqlite3
from dataclasses import dataclass
from datetime import datetime, date, time
from enum import Enum
from pydantic import BaseModel


class TransactionType(Enum):
    SPENT = 'spent'
    INCOME = 'income'


class CreateUserModel(BaseModel):
    name:str


class CreateTransactionModel(BaseModel):
    user_id:int
    t_type:TransactionType
    amount:int


connection_string = 'test.db'



@dataclass
class TransactionModel:
    id:int
    amount:int
    t_type:TransactionType
    t_date:date
    t_time:time

@dataclass
class UserModel:
    id:int
    name:str
    transactions:list[TransactionModel]|None 


@dataclass
class UserStatsModel():
    total_income:int
    total_spent:int


def add_user(name:str) -> int|None:
    with sqlite3.connect(connection_string) as conn:
        curs = conn.cursor()

        curs.execute('INSERT INTO users (name) VALUES (?)', (name,))

        return curs.lastrowid


def get_user(user_id:int) -> UserModel|None:
    with sqlite3.connect(connection_string) as conn:
        curs = conn.cursor()

        curs.execute('''
                        SELECT users.id, users.name, transactions.id, transactions.amount, transactions.type, transactions.datetime
                        FROM users
                        LEFT JOIN transactions ON users.id = transactions.user_id
                        WHERE users.id = ?
                    ''', (user_id,))

        rows = curs.fetchall()

        if not rows:
            return

        user = UserModel(id=rows[0][0], name=rows[0][1], transactions=[])

        if rows[0][2]:
            transactions_list = [TransactionModel(id=row[2], amount=row[3], t_type=row[4], t_date=datetime.fromtimestamp(row[5]).date() ,t_time=datetime.fromtimestamp(row[5]).time()) for row in rows]

            user.transactions = transactions_list 

        return user


def get_user_stat(user_id:int, date_start:datetime=datetime.fromtimestamp(0), date_finish:datetime=datetime.now()) -> UserStatsModel:
    with sqlite3.connect(connection_string) as conn:
        curs = conn.cursor()

        curs.execute("""
                        SELECT 
                            SUM(CASE WHEN type = 'INCOME' THEN amount ELSE 0 END) AS total_income,
                            SUM(CASE WHEN type = 'SPENT' THEN amount ELSE 0 END) AS total_expense
                        FROM transactions
                        WHERE user_id = ?
                    """, (user_id,)) 

        stats = curs.fetchone()
        
        user_stats = UserStatsModel(stats[0], stats[1])

        return  user_stats


def get_all_user(limit=50, page=1) -> list[UserModel]|None:
    with sqlite3.connect(connection_string) as conn:
        curs = conn.cursor()

        offset = (page - 1) * limit

        curs.execute('''
                        SELECT users.id, users.name, transactions.id, transactions.amount, transactions.type, transactions.datetime
                        FROM users
                        LEFT JOIN transactions ON users.id = transactions.user_id
                        LIMIT ? OFFSET ?
                    ''', (limit, offset))

        rows = curs.fetchall()

        if not rows:
            return 
        
        users = dict()

        for row in rows:

            user_id, name, transaction_id, amount, t_type, timestamp = row
            
            if user_id not in users:
                users[user_id] = UserModel(id=user_id, name=name, transactions=[]) 

            if transaction_id:
                dt = datetime.fromtimestamp(timestamp)
                users[user_id].transactions.append(TransactionModel(id=transaction_id, amount=amount, t_type=t_type, t_date=dt.date(), t_time=dt.time()))


        return list(users.values()) 


def add_transaction(user_id:int, t_type:TransactionType, amount:int) -> int|None:
    with sqlite3.connect(connection_string) as conn:

        dt = datetime.now().timestamp()

        curs = conn.cursor()

        curs.execute('INSERT INTO transactions (user_id, type, amount, datetime) VALUES (?, ?, ?, ?)', (user_id, t_type.name, amount, dt))

        return curs.lastrowid


def upd_user(user_id:int, user:CreateUserModel):
    with sqlite3.connect(connection_string) as conn:
        curs = conn.cursor()

        curs.execute('''
                     UPDATE users
                     SET name = ?
                     WHERE id = ?
                     ''', (user.name, user_id))
        


def upd_transaction(transaction_id:int, transaction:CreateTransactionModel):
    with sqlite3.connect(connection_string) as conn:
        curs = conn.cursor() 

        curs.execute('''
                     UPDATE transactions 
                     SET user_id = ?, amount = ?, type = ?
                     WHERE id = ?;
                     ''', (transaction.user_id, transaction.amount, transaction.t_type.name, transaction_id))



def del_user(user_id):
    with sqlite3.connect(connection_string) as conn:
        curs = conn.cursor()

        curs.execute('''
                     DELETE FROM transactions
                     WHERE user_id = ?
                     ''', (user_id,))
    
        curs.execute('''
                     DELETE FROM users
                     WHERE id = ?
                     ''', (user_id, ))


def del_transaction(transaction_id):
    with sqlite3.connect(connection_string) as conn:
        curs = conn.cursor()
        curs.execute('''
                     DELETE FROM transactions
                     WHERE id = ?
                     ''', (transaction_id,))


if __name__ == '__main__':
    with sqlite3.connect(connection_string) as conn:
        curs = conn.cursor()

        # Create User tableл
        curs.execute('''
                     CREATE TABLE IF NOT EXISTS users (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name VARCHAR(100)
                         )
                     ''')

        # Create Transaction table
        curs.execute('''
                     CREATE TABLE IF NOT EXISTS transactions (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         user_id INT FOREING KEY,
                         amount INT,
                         type VARCHAR(100),
                         datetime REAL
                         )
                     ''')

        curs.execute('PRAGMA foreign_keys = ON')



