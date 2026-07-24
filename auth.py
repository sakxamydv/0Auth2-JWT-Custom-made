from fastapi import FastAPI, HTTPException, status,Response,Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import secrets
from datetime import datetime, timezone, timedelta
from fastapi.responses import RedirectResponse
import jwt
SECRET_KEY = "my-super-secret-key-that-no-one-else-knows"
ALGORITHM = "HS256"
app = FastAPI()


REGISTERED_CLIENTS = {
    # Client 1: A  web app (canva)
    "canva_client_id_123": {
        "client_name": "Canva Design Suite",
        "client_secret": "canva_super_secret_key_456",
     
        "redirect_uris": [
            "http://localhost:5001/callback",
            "http://127.0.0.1:5001/callback"
        ]
    },
    # Client 2: A  music app (spotify)
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
        "password": "password123", 
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



@app.get("/authorize", response_class=HTMLResponse)
async def auth(client_id : str,redirect_uris:str,state: str = "",response_type: str = "code",):
    client = REGISTERED_CLIENTS.get(client_id)

    # Check if client exists
    if not client:
        raise HTTPException(status_code=404, detail="Client ID not found")

    # Check if redirect_uri is in the allowed list
    if redirect_uris not in client["redirect_uris"]:
        raise HTTPException(status_code=400, detail="Invalid redirect URI")


    if response_type != "code":
        raise HTTPException(status_code=400, detail="Only response_type=code is supported")

    return f"""

    <html>
        <body>
            <h2>Sign in with MyOAuth</h2>
            <p>App <strong>{client['client_name']}</strong> wants to access your account.</p>
            
            <form method="post" action="/authorize">
                <input type="hidden" name="client_id" value="{client_id}">
                <input type="hidden" name="redirect_uris" value="{redirect_uris}">
                <input type="hidden" name="state" value="{state}">

                <input type="text" name="username" placeholder="Username" required><br><br>
                <input type="password" name="password" placeholder="Password" required><br><br>
                
                <button type="submit">Log In & Authorize</button>
            </form>
        </body>
    </html>
    """



@app.post("/authorize", response_class=HTMLResponse)
async def auth(username :str =Form(...),password:str=Form(...),state:str=Form(...)):
    user = USERS.get(username)

    # Check if client exists
    if not user:
        raise HTTPException(status_code=404, detail="Client ID not found")

    if password != user["password"]:
        raise HTTPException(status_code=400, detail="Invalid password")
    auth_code = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    # 3. Save to your in-memory dictionary
    AUTHORIZATION_CODES[auth_code] = {
        "client_id": user["client_id"],
        "redirect_uri": user["redirect_uris"],
        "username": username,
        "expires_at": expires_at}   
    redirect_url = f"{user["redirect_uris"]}?code={auth_code}&state={state}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@app.post("/token")
async def token(grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uris: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...)):

    client = REGISTERED_CLIENTS.get(client_id)

    # Check if client exists
    if not client:
        raise HTTPException(status_code=404, detail="Client ID not found")
    if redirect_uris not in client["redirect_uris"]:
            raise HTTPException(status_code=400, detail="Invalid redirect URI")
    if client_secret not in client["client_secret"]:
            raise HTTPException(status_code=400, detail="error")
    if code not in AUTHORIZATION_CODES:
        raise HTTPException(status_code=400, detail="invalid code")
    session = AUTHORIZATION_CODES["code"]
    if session["expires_at"] >= datetime.now(timezone.utc):
         raise HTTPException(status_code=400, detail="TOKEN EXPIRED")


now = datetime.now(timezone.utc)

payload = {
    "name": "alice",                          # Logged in user
    "client_id": "canva_client_id_123",       # Third-party app
    "iat": now,                               # Issue time
    "exp": now + timedelta(minutes=15)        # Expires in 15 minutes
}

# 3. Generate (encode) the JWT
encoded_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

print(encoded_token)
