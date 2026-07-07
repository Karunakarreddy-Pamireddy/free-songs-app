import os
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import jwt

from app.config import settings
from app.auth import verify_password, create_access_token, pwd_context

app = FastAPI(
    title="FreeSongs API", 
    description="High-performance asynchronous streaming engine with automated AI upload endpoints."
)

# Cross-Origin Resource Sharing configuration allowing your web and mobile apps to communicate safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secure Seed Application Administrator Credentials (We will port this to an DB layer on Day 12)
USER_DB = {
    "admin": pwd_context.hash("admin123")
}

# --- AUTHENTICATION ROUTE ---

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Validates login credentials and returns a secure 24-hour access token."""
    user_hash = USER_DB.get(form_data.username)
    if not user_hash or not verify_password(form_data.password, user_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validates the incoming JWT bearer token before granting access to secure endpoints."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# --- HIGH-PERFORMANCE AUDIO STREAMING ROUTE ---

@app.get("/stream/{song_name}")
async def stream_song(song_name: str):
    """
    Streams audio files asynchronously in chunks.
    Prevents server memory exhaustion and eliminates buffering lags.
    """
    file_path = os.path.join(settings.SONGS_DIR, song_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested song file not found on server")
    
    # Asynchronous generator to read the audio track in chunks (1024 bytes per step)
    def chunk_generator():
        with open(file_path, mode="rb") as audio_file:
            while chunk := audio_file.read(1024 * 64):  # 64 KB Chunks
                yield chunk

    return StreamingResponse(chunk_generator(), media_type="audio/mpeg")

# --- FILE DOWNLOAD ROUTE ---

@app.get("/download/{song_name}")
async def download_song(song_name: str):
    """Directly delivers the audio asset as a single clean downloadable file attachment."""
    file_path = os.path.join(settings.SONGS_DIR, song_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested song file not found on server")
        
    return FileResponse(
        path=file_path, 
        filename=song_name, 
        media_type="application/octet-stream"
    )



# ... (Keep all your Day 4 imports, configurations, and authentication routes exactly the same)

# --- MUSIC & AUTOMATED UPLOAD ENDPOINTS ---

@app.post("/upload-song/", status_code=status.HTTP_201_CREATED)
async def upload_song(
    file: UploadFile = File(...), 
    current_user: str = Depends(get_current_user)
):
    """
    Automated backend endpoint for AI systems or upload bots.
    Requires a valid JWT Bearer Token in the authorization header.
    """
    # Ensure target storage volume exists
    os.makedirs(settings.SONGS_DIR, exist_ok=True)
    
    # Clean the file name and establish the target write path
    file_path = os.path.join(settings.SONGS_DIR, file.filename)
    
    # Read incoming binary data stream and write it asynchronously to storage
    try:
        with open(file_path, "wb") as buffer:
            # Read and write chunks to handle large audio files smoothly
            while content := await file.read(1024 * 64):  # 64 KB chunks
                buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write audio asset to disk: {str(e)}"
        )
        
    return {
        "status": "success",
        "filename": file.filename,
        "uploader": current_user,
        "message": "Audio asset automatically ingested to cloud storage disk."
    }

# --- HIGH-PERFORMANCE AUDIO STREAMING ROUTE ---
# ... (Keep your @app.get("/stream/{song_name}") and @app.get("/download/{song_name}") from Day 4)


# ... (Keep all your existing configuration, auth, and upload imports at the top)
from app.analytics_engine import log_user_activity  # <-- Add this new import statement

# ... (Keep your /token, get_current_user, and /upload-song/ endpoints exactly as they are)

# --- HIGH-PERFORMANCE AUDIO STREAMING ROUTER ---

@app.get("/stream/{song_name}")
async def stream_song(song_name: str):
    """Streams audio files asynchronously in chunks while logging streaming telemetry."""
    file_path = os.path.join(settings.SONGS_DIR, song_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested song file not found on server")
    
    # Trigger tracking engine hook for real-time analytics
    log_user_activity(song_name=song_name, action_type="stream")  # <-- Add this tracking hook
    
    def chunk_generator():
        with open(file_path, mode="rb") as audio_file:
            while chunk := audio_file.read(1024 * 64):
                yield chunk

    return StreamingResponse(chunk_generator(), media_type="audio/mpeg")

# --- FILE DOWNLOAD ROUTER ---

@app.get("/download/{song_name}")
async def download_song(song_name: str):
    """Delivers the audio asset as an attachment while logging download telemetry."""
    file_path = os.path.join(settings.SONGS_DIR, song_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested song file not found on server")
        
    # Trigger tracking engine hook for real-time analytics
    log_user_activity(song_name=song_name, action_type="download")  # <-- Add this tracking hook
        
    return FileResponse(
        path=file_path, 
        filename=song_name, 
        media_type="application/octet-stream"
    )