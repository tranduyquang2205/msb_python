from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from msb import MSB
import sys
import traceback
from api_response import APIResponse

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
    try:
        msb = MSB(input.username, input.password,input.account_number)
        session_raw = msb.login()
        return APIResponse.json_format(session_raw)
    except Exception as e:
        response = str(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        return APIResponse.json_format(response)

@app.post('/get_balance', tags=["get_balance"])
def get_balance_api(input: LoginDetails):
    try:
        msb = MSB(input.username, input.password,input.account_number)
        balance = msb.get_balance()
        return APIResponse.json_format(balance)
    except Exception as e:
        response = str(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        return APIResponse.json_format(response)
    
class Transactions(BaseModel):
    username: str
    password: str
    account_number: str
    from_date: str
    to_date: str
    
@app.post('/get_transactions', tags=["get_transactions"])
def get_transactions_api(input: Transactions):
    try:
        msb = MSB(input.username, input.password,input.account_number)
        transactions = msb.get_transactions(input.from_date,input.to_date)
        return APIResponse.json_format(transactions)
    except Exception as e:
        response = str(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        return APIResponse.json_format(response)
    
if __name__ == "__main__":
    uvicorn.run(app ,host='0.0.0.0', port=3000)