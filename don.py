from fastapi import FastAPI, Request
from functions import *
from fastapi.middleware.cors import CORSMiddleware
import uuid




sheetid="1EAl0Pb-ehUa8iX_f6O265Kdjkf0UIsRkZLEVNdW7bVo"




app = FastAPI()

email=str(get_spreadsheet_email(sheetid))
paswrd=str(get_spreadsheet_pass(sheetid))




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace '*' with the specific URL of your React app in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/")
def read_root():
    return {"Hello": "User"}

targetswitch=get_spreadsheet_target(sheetid)


app.get("/updatetarget")
async def updatetarget():
    targetswitch=get_spreadsheet_target(sheetid)
    return {"Target": targetswitch}


@app.post("/receivepledge")
async def recievepledge(request: Request):
    checkresponse(email,paswrd)
    login_response=get_login_response_by_id(1)
    
    data = await request.json()
    
    print("1")
    unique_id = str(uuid.uuid4())
    name,ammount=getdetails(data,login_response)
    if targetswitch:
        add_or_update_donation(1,ammount)
    
    
            
    pledge_id=add_pledge(name, ammount)
    print(pledge_id)
    
    requests.get(f"https://absocket.onrender.com/updateui?donorid={pledge_id}")
    
    
    

    print("WEBHOOK DATA RECEIVED:")
    
    return {
        "data": data
    }