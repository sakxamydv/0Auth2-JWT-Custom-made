from fastapi import FastAPI, HTTPException, status,Response,Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import secrets
from datetime import datetime, timezone, timedelta
from fastapi.responses import RedirectResponse
import jwt
SECRET_KEY = "8e1f04a4029703d133f888505a9d1bcc71a46a6d40a1f8efe3b758b2bc7cc3fc" #bad practice kept it like this just for now.
ALGORITHM = "HS256"
app = FastAPI()

REGISTERED_CLIENTS = {
  
    "canva_client_id_123": {
        "client_name": "Canva Design Suite",
        "client_secret": "canva_super_secret_key_456",
        # Only redirects listed here will be accepted by /authorize
        "redirect_uris": [
            "http://localhost:5001/callback",
            "http://127.0.0.1:5001/callback"
        ]
    },

    "spotify_client_id_789": {
        "client_name": "Spotify Player",
        "client_secret": "spotify_super_secret_key_000",
        "redirect_uris": [
            "http://localhost:5002/oauth/callback"
        ]
    }
}



USERS = {
    "alice": {
        "password": "password123",  # In real life, this would be a hashed password
        "full_name": "Alice Smith",
        "email": "alice@example.com",
        "picture": "https://api.dicebear.com/7.x/bottts/svg?seed=Alice"
    },
    "bob": {
        "password": "securepassword456",
        "full_name": "Bob Jones",
        "email": "bob@example.com",
        "picture": "https://api.dicebear.com/7.x/bottts/svg?seed=Bob"
    }
}



AUTHORIZATION_CODES = {}



@app.get("/authorize", response_class=HTMLResponse) # Here we VALIDATES THE SERVICE and if it's legit we moveon to ask credentials from user to verify them in post./authorize
async def auth(client_id : str,redirect_uris:str,state: str = "",response_type: str = "code",):
    client = REGISTERED_CLIENTS.get(client_id)

    # Check if client exists
    if not client:
        raise HTTPException(status_code=404, detail="Client ID not found")

    # Check if redirect_uri is in the allowed list
    if redirect_uris not in client["redirect_uris"]:
        raise HTTPException(status_code=400, detail="Invalid redirect URI")


    if response_type != "code":
        raise HTTPException(status_code=400, detail="Only response_type=code is supported") #login page

    return f"""       

    <html>
        <body>
            <h2>Sign in with MyOAuth</h2>
            <p>App <strong>{client['client_name']}</strong> wants to access your account.</p>
            
            <form method="post" action="/authorize">                     
                <input type="hidden" name="client_id" value="{client_id}">
                <input type="hidden" name="redirect_uris" value="{redirect_uris}">
                <input type="hidden" name="state" value="{state}">

                <input type="text" name="username" placeholder="alice" required><br><br>
                <input type="password" name="password" placeholder="password123" required><br><br>
                
                <button type="submit">Log In & Authorize</button>
            </form>
        </body>
    </html>
    """
# in the above html page we take the users input and send it to post authorize using post method and we validates the user data from our database


@app.post("/authorize", response_class=HTMLResponse) #validate sthe users credentials
async def auth(client_id: str = Form(...),
    redirect_uris: str = Form(...),
    state: str = Form(""),
    username: str = Form(...),
    password: str = Form(...)):
    user = USERS.get(username)

    # Check if client exists
    if not user:
        raise HTTPException(status_code=404, detail="Client ID not found")

    if password != user["password"]:
        raise HTTPException(status_code=400, detail="Invalid password")
    auth_code = secrets.token_urlsafe(32)   #creating a auth token for client 
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10) #creating expiration date for auth token
    # 3. creating and saving authcode dictonary and sending it to client 
    AUTHORIZATION_CODES[auth_code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uris,
        "username": username,
        "expires_at": expires_at
    }
    redirect_url = f"{redirect_uris}?code={auth_code}&state={state}" # here we are sending our data in a form of url to callback get method as mentioned in upper redirect urls
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND) #send the auth token to client server


@app.post("/token") #after client recives the auth token in a url (get method)it again sends back the auth token to post token to verify it again in backend and then it calls the post token method to creat a jwt toke and burn the auth token forever
async def token(grant_type: str = Form(...),
    code: str = Form(...),
    state: str | None = Form(None),
    redirect_uris: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...)):

    client = REGISTERED_CLIENTS.get(client_id)

    # Check if client exists
    if not client:
        raise HTTPException(status_code=404, detail="Client ID not found")
    if redirect_uris not in client["redirect_uris"]:
            raise HTTPException(status_code=400, detail="Invalid redirect URI")
    if client_secret != client["client_secret"]:
            raise HTTPException(status_code=400, detail="error")
    if code not in AUTHORIZATION_CODES:
        raise HTTPException(status_code=400, detail="invalid code")
    session = AUTHORIZATION_CODES[code]
    if session["expires_at"] <= datetime.now(timezone.utc):
         raise HTTPException(status_code=400, detail="TOKEN EXPIRED")


    now = datetime.now(timezone.utc)

    payload = {
        "name": session["username"],                          # Logged in user
        "client_id": session["client_id"],       # Third-party app
        "iat": now,                               # Issue time
        "exp": now + timedelta(minutes=15)        # Expires in 15 minutes
    }

    # 3. Generate (encode) the JWT
    encoded_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM) #encoding the jwt token

    return {
        "access_token": encoded_token,
        "token_type": "bearer",
        "expires_in": 900
    }
