from datetime import datetime
import requests
import urllib
import pandas as pd

def filter_transactions_by_limit(data, mostrecent):
    """
    Filters transactions to return the most recent `mostrecent` number of transactions.

    :param data: Dictionary containing the transactions.
    :param mostrecent: Integer representing the number of most recent transactions to return.
    :return: Filtered dictionary with only the most recent `mostrecent` transactions.
    """
    def parse_created_date(date_str):
        # Normalize the ISO format if fractional seconds have two digits
        if '.' in date_str:
            parts = date_str.split('.')
            parts[1] = parts[1].ljust(3, '0')  # Pad fractional seconds to 3 digits
            date_str = '.'.join(parts)
        return datetime.fromisoformat(date_str)

    # Get the transactions and sort them by createdDate in descending order
    transactions = sorted(
        data.get('pledgeTransGridModel', []),
        key=lambda x: parse_created_date(x['createdDate']),
        reverse=True
    )

    # Limit the number of transactions to `mostrecent`
    limited_transactions = transactions[:mostrecent]

    # Return the filtered dictionary
    return limited_transactions


def get_spreadsheet_email(sheet_id):
    """
    Fetches the email from cell B2 of a public Google Sheet.
    
    Parameters:
        sheet_id (str): The ID of the Google Sheet (found in the sheet's URL).
    
    Returns:
        str: The email from cell B2.
    """
    # Construct the CSV URL
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    # Read the data into a DataFrame
    data = pd.read_csv(csv_url)
    
    # Extract and return the email from the second column (B2)
    email = data.iloc[0, 1]  # Assuming B2 corresponds to index 0, column 1
    return email


def get_spreadsheet_pass(sheet_id):
    """
    Fetches the password from cell B3 of a public Google Sheet.
    
    Parameters:
        sheet_id (str): The ID of the Google Sheet (found in the sheet's URL).
    
    Returns:
        str: The password from cell B3.
    """
    # Construct the CSV URL
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    # Read the data into a DataFrame
    data = pd.read_csv(csv_url)
    
    # Extract and return the password from the third column (B3)
    password = data.iloc[1, 1]  # Assuming B3 corresponds to index 1, column 1
    return password


def make_captcha_request(anchor,varChr,varVh,varBg):
    anchorr = str(anchor)
    anchorr = anchorr.strip()
    keysite = anchorr.split('k=')[1].split("&")[0]
    var_co = anchorr.split("co=")[1].split("&")[0]
    var_v = anchorr.split("v=")[1].split("&")[0]

    r1 = requests.get(anchorr).text

    token1 = r1.split('recaptcha-token" value="')[1].split('">')[0]

    var_chr = str(varChr)
    var_vh = str(varVh)
    var_bg = str(varBg)
    var_chr = str(urllib.parse.quote(var_chr))
    

    payload = {
        "v":var_v,
        "reason":"q",
        "c":token1,
        "k":keysite,
        "co":var_co,
        "hl":"en",
        "size":"invisible",
        "chr":var_chr,
        "vh":var_vh,
        "bg":var_bg
    }

    r2 = requests.post("https://www.google.com/recaptcha/api2/reload?k={}".format(keysite), data=payload)
    try:
        token2 = str(r2.text.split('"rresp","')[1].split('"')[0])
    except:
        token2 = 'null'

    if token2 == "null":
        print("\nRecaptcha not vulnerable : \n\n"+str(r2.text))
        
    else:
       
        returnanchor=anchorr
        returnrelod=f"https://www.google.com/recaptcha/api2/reload?k={keysite}"
        returnpayload=f"v={var_v}&reason=q&c=<token>&k={keysite}&co={var_co}&hl=en&size=invisible&chr={var_chr}&vh={var_vh}&bg={var_bg}"
            
        return returnanchor,returnrelod,returnpayload
    
def generateresponse(anchorurl, reloadurl, payload):
    s = requests.Session()
    r1 = s.get(anchorurl).text
    token1 = r1.split('recaptcha-token" value="')[1].split('">')[0]
    payload = payload.replace("<token>", str(token1))
    r2 = s.post(reloadurl, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        token2 = str(r2.text.split('"rresp","')[1].split('"')[0])
        return token2
    except:
        return ""
    
    

def login_function(email,password,response_token):
# API URL
    url = "https://webapi.donary.com/v2/authentication/login"

    # Payload for login, replace with actual email, password, and generated reCAPTCHA token
    payload = {
        "email":email ,
        "password": password,
        "recapcha": response_token  
    }

    # Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Make the POST request
    response3 = requests.post(url, json=payload, headers=headers)

    # Check the response status and content
    if response3.status_code == 200:
        
        return response3  # This will show the server's response
    else:
        print("Login failed. Status code:", response3.status_code)
        print("Response:", response3.text)  # Print the error message from the server
        
        

def get_pled(login_response):
    # Define the API endpoint
    url = "https://webapi.donary.com/v1/pledgetransaction/getPledgeTrans"

    # Extract the access token from the login response
    access_token = login_response.json().get("accessToken")

    # Set the request headers with the access token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    event_guid=login_response.json().get("eventGuid")
    # Define the payload with the eventGuId
    payload = {
        "eventGuId": event_guid
    }

    # Send the POST request
    response = requests.post(url, headers=headers, json=payload)

    # Check and handle the response
    if response.status_code == 200:
        
        return response.json()
    else:
        print("Failed to retrieve donors:", response.status_code, response.text)
        return {"error": response.text, "status_code": response.status_code}
    


def donary_login(email,paswrd):
    anchorresult,reloadurlresult,payloadresult=make_captcha_request('https://www.google.com/recaptcha/enterprise/anchor?ar=1&k=6Le5HB8qAAAAACVrDjBtWwnN3Ry5W1zCoV8EZoCj&co=aHR0cHM6Ly9wLmRvbmFyeS5jb206NDQz&hl=en&v=EGbODne6buzpTnWrrBprcfAY&size=invisible&cb=mqhzibkq69xi','',' 6009931042','!XFqgWl8KAAQeBu1XbQEHewF3r1uHI2K6ioroh_8HdshF71OdCl_0vnUsr-qyUE10ZEWjb1fCAv0LouH4kuXjiiXDFrqSLfTtFreWo6uV426VFvd5MCviCasLbH2YDKGpv6jmLk7NF_wJIku84MwyGF2Cdxg4TBATPN50ZYOudlADShMS9CuXpKZ-VC45Ggs_JeDRga0qHGpmqyJAHzwl9BLSeCqieRgtMnSS7oDzJ5vN8jKBjKEHkAWKF-W7sZVQ5NlFATCkv61-poyB_6QqCmqBYGFF2NTikI6HNiR9A-JTwc3InKXygJFr5_vrddsFXrGRAX0no1SWeHUt7uT1juwraHeueD2dDKBkH22_D8coA12A-CfvtdOh1aEjIdWD7L9t3DksdYW5hjN6VoahPGdJctCc4mYQNUxuuCsX4ddzGONH-opywCM3Z_SKs866t7leSfRor9_nnc4tZqGUX118Ij5bIAb4evGrRbi8p1o0-YWNWdUPYU1rDCSXZPZB28i1ENZ11xTGnARUy77eogCECHFreyXShCjHp87rqwRwj0vDcvk6aRs9Xd1EouLwL1iegUh1-xjXIyjUu2zjwreTc7KpssIg0nEeoxMt1WhmKqo3AsC2iOy3ScvSv7Kwb5lKJaTzEcjcpcoHLWykk90J-C-Z1sEGaCFZ-VFZoSNLceWEKKVubS_iWPeHQGXkXHduMSc1osY4bLx6MoDc_4H8C6X8IxEUcYvRAqkAIoiTDsoYBBgFxOWFQ-E4bbfHz2_wnhBntUx3OWqxp4wWYSq6UTt79nNXHQ-r8WmWUd6_pxtV3fhnF3BrHJ8xJwn_46v6giTAzZyhWSm1_Cwbc2PO4G4l0LEk-g5z7Y333BlIXJ7v1O1wxRsJpFVVGBvKTt48rkMgvrsoiklkJoHRDunpYjuIVpQl-8eTbpK4eunQ6i-hTy5dkPDRCXHiQTnrNWOuEjNhIxfLK86jc1XdETdm5ZxLkAMQ7QcvF-V2FY_4AwLQhKeNWT0r80YYcX3qgMGF4UvW4EMWLGxjh5PIvuWUW40In9r-i48-vgmQe8xEY4kn8yhNhe9eWjYDf2U1Ibzqf2FCRta1gR0-zQhQa40yXW_xTrRR6kMJnb_5SSbZ8BGWr1O00RRNkoYOv5cBdNIZLq_586UsCMRCHt_Bfi8wy-lcBCskMnXsl-XGclOYJ7RN0NIKVsXQycvd6WuWSjKk7ET31XZtkSDL-3VRwx1qP8k4be23oY_NgG4kcd8XcnlvXbf5g0EnJJWxKFqQGc3eM9HpDKZrQzSodziPWXYVB96aLcPx7neaQ_XRlNKa8klHjJnqt1dAtfvMFzqEcAvW0i-PX0bzaoxvILlkMYLNPIucK5McUrxCI_OdpPHN6FJjDqfzjLhofVFYe9pdeSVKDJpz6uEoGSzcawFUXTVvN2_fWRFQ8Jr-0uOBMSgc8Rr2G1LJxbtz-EFzDv6xEbvQgaIWvQvwU9dR-QsJZe4A8kc7ciQ96chifCgaJ5tOdtbELddABgC9mVGwRGVQ_aXxvwm84F2PjkcyDI-LQMFqFxz36qaO28CQ-KhigujZE9w77_sBBKrbjtMKX-MADNYpYUQyHUI7eXAWIOtpOrFlSnaGwPOtJRO6ohhJbK2cUPevOva9QrVvnYPOOYkloXKlIZNhhCikHJRP_8k6361N0E3NCe_XewdhO1_XMydkAIL6BKNO1s_JzUrdo0fYlgZvgRoCuqTBilP-bwNXFh80IvsC9DH6AJwKt4fx3Qc3V0u8coxE8z9biHbD6KKCBP8pUfoZd9EnMEL1U-OB48lK1TENzy_u6_KsAKfOlD8oebo8NMiurlfhiRtkUHVrPT5qPxRC-iACQAU1THIwr7PNwTwXI3rmnxEk9riXYefT0nzaJ5X9v-hI0upcQ_t7TE6_laNh3Rto0B3ESRa5haT1QQol7NgquPH3h2LwGdPF4ncmNV04tZYb6R9WxHWJ7cA-xN1r1hZ9pFMbk9gIiQ*')
    
    
    respnsetoken=generateresponse(anchorresult,reloadurlresult,payloadresult)
    
    
    login_response=login_function(str(email),str(paswrd),respnsetoken)
    
    return login_response