from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import httpx
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],  # Allow requests from Live Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../frontend/static", html=True), name="static")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Spotify API endpoints
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"

SCOPE = "user-read-recently-played playlist-modify-public user-top-read"



@app.get("/")
async def serve_frontend():
    return FileResponse("../frontend/static/index.html")

@app.get("/login")
async def login():
    # Redirect to Spotify's authorization page
    auth_url = (
        f"{SPOTIFY_AUTH_URL}?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope={SCOPE}"
    )
    return RedirectResponse(url=auth_url)

@app.get("/callback")
async def callback(code: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )
        print(response.text)  # Log the response for debugging
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch access token")

        token_data = response.json()
        return JSONResponse(content=token_data)

@app.post("/refresh-token")
async def refresh_token(refresh_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to refresh token")
        token_data = response.json()
        return {"access_token": token_data["access_token"]}
    

#http://localhost:8000/profile?access_token=
@app.get("/profile")
async def get_profile(access_token: str):
    # Fetch user profile using the access token
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SPOTIFY_API_BASE_URL}/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch profile")

        return response.json()

#http://localhost:8000/top-items-artists?access_token=
@app.get("/top-items-artists")
async def get_profile_top_artists(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SPOTIFY_API_BASE_URL}/me/top/artists",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"time_range": "medium_term", "limit": "10", "offset": "5"},
        )
        if response.status_code != 200:
            print(response.text)
            raise HTTPException(status_code=400, detail="Failed to fetch user top items")
        return response.json()

#http://localhost:8000/top-items-tracks?access_token=
@app.get("/top-items-tracks")
async def get_profile_top_tracks(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SPOTIFY_API_BASE_URL}/me/top/tracks",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"time_range": "medium_term", "limit": "10", "offset": "5"},
        )
        if response.status_code != 200:
            print(response.text)
            raise HTTPException(status_code=400, detail="Failed to fetch user top tracks")
        return response.json()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)