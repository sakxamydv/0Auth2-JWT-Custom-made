from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
import jwt
from fastapi import HTTPException, Header, Depends

SECRET_KEY = "8e1f04a4029703d133f888505a9d1bcc71a46a6d40a1f8efe3b758b2bc7cc3fc"
ALGORITHM = "HS256"
app = FastAPI(title="Client App (Canva)")

CLIENT_ID = "canva_client_id_123"
CLIENT_SECRET = "canva_super_secret_key_456"
REDIRECT_URI = "http://localhost:5001/callback"
AUTH_SERVER_URL = "http://127.0.0.1:8000"



@app.get("/", response_class=HTMLResponse)
async def home():
    # Step 1: User clicks "Login with OAuth"
    auth_url = f"{AUTH_SERVER_URL}/authorize?client_id={CLIENT_ID}&redirect_uris={REDIRECT_URI}&response_type=code&state=xyz123"
    return f"""
    <html>
        <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
            <h1>Lets Pretend this is Canva!</h1>
            <a href="{auth_url}">
                <button style="padding: 12px 24px; background-color: #4CAF50; color: white; font-size: 16px; border: none; border-radius: 4px; cursor: pointer;">
                    Log in with OAuth Server [eg : GOOGLE]
                </button>
            </a>
        </body>
    </html>
    """

@app.get("/callback", response_class=HTMLResponse)
async def callback(code: str, state: str = ""):
    # Step 2: Client app receives code and calls POST /token on Auth Server behind the scenes
    async with httpx.AsyncClient() as client:
        response = await client.post( 
            f"{AUTH_SERVER_URL}/token",
            data={
                "grant_type": "authorization_code", #sending auth token to backend post token for verfication
                "code": code,
                "redirect_uris": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            }
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {response.text}")

    token_data = response.json()          #taking the response an converting it to json
    access_token = token_data.get("access_token") #accessing the token 
    decoded_user_data = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM]) #decoding it 
#priniting it 
    return f"""
    <html>
        <body style="font-family: sans-serif; padding: 40px;">
            <h2>🎉 Login Successful!</h2>
            <p><strong>Raw Encoded JWT:</strong></p>
            <textarea rows="3" cols="80" readonly>{access_token}</textarea>
            
            <h3>🔓 Decoded JWT Payload (JSON Data):</h3>
            <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px;">{decoded_user_data}</pre>
        </body>
    </html>
    """
