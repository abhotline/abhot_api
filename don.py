from fastapi import FastAPI, Request
from functions import *
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace '*' with the specific URL of your React app in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sheetid="1EAl0Pb-ehUa8iX_f6O265Kdjkf0UIsRkZLEVNdW7bVo"

email=get_spreadsheet_email(sheetid)
psrd=get_spreadsheet_pass(sheetid)

@app.get("/pledges/")
def get_pledges():

    login_response=donary_login(email,psrd)
    pledges=get_pled(login_response)
    pledges=filter_transactions_by_limit(pledges, 5)

    return pledges

@app.post("/recivepledge")
async def recievepledge(request: Request):
    data = await request.json()
    print("WEBHOOK DATA RECEIVED:")
    print(data)
    return {
        "data": data
    }

