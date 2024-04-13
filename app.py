from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from msb import MSB


msb = MSB()
app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}
class LoginDetails(BaseModel):
    username: str
    password: str
    account_number: str
    
@app.post('/login', tags=["login"])
def login_api(input: LoginDetails):
        session_raw = msb.login(input.username, input.password)
        return (session_raw)

@app.post('/get_balance', tags=["get_balance"])
def get_balance_api(input: LoginDetails):
        accounts_list = msb.get_accounts_list()
        balance = msb.get_balance(input.account_number)
        return (balance)
    
class Transactions(BaseModel):
    username: str
    password: str
    account_number: str
    from_date: str
    
@app.post('/get_transactions', tags=["get_transactions"])
def get_transactions_api(input: Transactions):
        transactions = msb.get_transactions(input.account_number,input.from_date)
        return (transactions)
    
if __name__ == "__main__":
    uvicorn.run(app ,host='0.0.0.0', port=3000)