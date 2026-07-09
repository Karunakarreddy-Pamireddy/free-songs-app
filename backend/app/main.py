import os
from typing import Optional
from datetime import datetime, timezone
import pandas as pd
import jwt

from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.auth import verify_password, create_access_token, pwd_context
from app.analytics_engine import log_user_activity

app = FastAPI(
    title="FreeSongs API", 
    description="High-performance asynchronous streaming engine with automated AI upload endpoints."
)

# Cross-Origin Resource Sharing (CORS) Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Static Administration Credential Database Seed
USER_DB = {
    "admin": pwd_context.hash("admin123")
}

# --- AUTHENTICATION DEPENDENCY ROUTING ---

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

# --- MUSIC & AUTOMATED UPLOAD ROUTES ---

@app.post("/upload-song/", status_code=status.HTTP_201_CREATED)
async def upload_song(
    file: UploadFile = File(...), 
    current_user: str = Depends(get_current_user)
):
    """Automated backend endpoint for AI systems or upload bots."""
    os.makedirs(settings.SONGS_DIR, exist_ok=True)
    file_path = os.path.join(settings.SONGS_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
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

@app.get("/stream/{song_name}")
async def stream_song(song_name: str):
    """Streams audio files asynchronously in chunks while logging telemetry."""
    file_path = os.path.join(settings.SONGS_DIR, song_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested song file not found on server")
    
    log_user_activity(song_name=song_name, action_type="stream")
    
    def chunk_generator():
        with open(file_path, mode="rb") as audio_file:
            while chunk := audio_file.read(1024 * 64):
                yield chunk

    return StreamingResponse(chunk_generator(), media_type="audio/mpeg")

@app.get("/download/{song_name}")
async def download_song(song_name: str):
    """Delivers the audio asset as an attachment while logging download telemetry."""
    file_path = os.path.join(settings.SONGS_DIR, song_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested song file not found on server")
        
    log_user_activity(song_name=song_name, action_type="download")
        
    return FileResponse(
        path=file_path, 
        filename=song_name, 
        media_type="application/octet-stream"
    )

# --- ADMINISTRATIVE DATA ANALYTICS ROUTES ---

@app.get("/analytics/summary", status_code=status.HTTP_200_OK)
async def get_platform_summary(
    window_days: Optional[int] = None,
    current_user: str = Depends(get_current_user)
):
    """Parses and filters live tracking logs within a dynamic time window using pandas."""
    if not os.path.exists(settings.ANALYTICS_FILE):
        return {
            "total_engagements": 0,
            "top_tracks": {},
            "action_distribution": {"stream": 0, "download": 0}
        }
    
    try:
        df = pd.read_csv(settings.ANALYTICS_FILE)
        if df.empty:
            return {
                "total_engagements": 0,
                "top_tracks": {},
                "action_distribution": {"stream": 0, "download": 0}
            }
            
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        if window_days is not None:
            now = pd.Timestamp.now(tz='UTC').tz_localize(None)
            start_bound = now - pd.Timedelta(days=window_days)
            df = df[df['timestamp'] >= start_bound]
            
        total_engagements = len(df)
        top_tracks = df['song_name'].value_counts().head(5).to_dict()
        action_distribution = df['action'].value_counts().to_dict()
        
        return {
            "time_window_applied": f"{window_days} days" if window_days else "All-Time",
            "total_engagements": total_engagements,
            "top_tracks": top_tracks,
            "action_distribution": action_distribution
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Time-series window calculation failure: {str(e)}"
        )

    # ... (Keep your top import blocks, but add these database imports)
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models import DBUser

# Generate the physical tables automatically on server launch if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FreeSongs API")

# --- AUTO-SEED ROOT ADMIN USER IF MISSING ---
# We write a quick startup seed block to ensure an admin account always exists
with SessionLocal() if 'SessionLocal' in globals() else engine.connect() as conn:
    from app.database import SessionLocal
    db = SessionLocal()
    if not db.query(DBUser).filter(DBUser.username == "admin").first():
        admin_user = DBUser(username="admin", hashed_password=pwd_context.hash("admin123"))
        db.add(admin_user)
        db.commit()
    db.close()

# ... (Keep CORS middleware setups exactly as they are)

# --- REFACTORED AUTHENTICATION ROUTERS ---

@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)  # <-- Inject database dependency here
):
    """Validates login credentials against the persistent SQLite database."""
    # Look up user inside the physical user table
    user = db.query(DBUser).filter(DBUser.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Validates token and double-checks the active user still exists in the database table."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
            
        # Verify user still stands inside the formal system
        user = db.query(DBUser).filter(DBUser.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User database mismatch")
            
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# ... (Keep your /upload-song/, /stream/, /download/, and /analytics/ summary routes exactly as they are!)

# ... (Keep all your existing top imports exactly the same)
from app.rate_limiter import rate_limit_guard  # <-- Add this import statement

# ... (Keep your tables compilation, app initialization, and /token /upload routes exactly as they are)

# --- REFACTORED HIGH-PERFORMANCE AUDIO STREAMING ROUTER ---

@app.get("/stream/{song_name}")
async def stream_song(
    song_name: str, 
    _ = Depends(rate_limit_guard)  # <-- Inject the rate-limit guard dependency right here!
):
    """Streams audio files asynchronously in chunks while being guarded by active rate-limiting."""
    file_path = os.path.join(settings.SONGS_DIR, song_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested song file not found on server")
    
    log_user_activity(song_name=song_name, action_type="stream")
    
    def chunk_generator():
        with open(file_path, mode="rb") as audio_file:
            while chunk := audio_file.read(1024 * 64):
                yield chunk

    return StreamingResponse(chunk_generator(), media_type="audio/mpeg")


@app.get("/download/{song_name}")
async def download_song(
    song_name: str, 
    _ = Depends(rate_limit_guard)  # <-- Inject the rate-limit guard dependency right here!
):
    """Delivers the audio asset as an attachment while being guarded by active rate-limiting."""
    file_path = os.path.join(settings.SONGS_DIR, song_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested song file not found on server")
        
    log_user_activity(song_name=song_name, action_type="download")
        
    return FileResponse(
        path=file_path, 
        filename=song_name, 
        media_type="application/octet-stream"
    )

# ... (Leave the remaining analytics summary endpoint code at the bottom completely untouched)

# --- ADD THIS ROUTE INSIDE YOUR MUSIC ENDPOINTS SECTION ---

@app.get("/songs")
async def get_all_songs():
    """Scans the storage directory and returns a list of all available audio assets."""
    if not os.path.exists(settings.SONGS_DIR):
        return []
    
    # Filter the directory to pull only mp3 assets
    songs = [f for f in os.listdir(settings.SONGS_DIR) if f.endswith(".mp3")]
    return sorted(songs)

@app.get("/songs")
async def get_all_songs():
    """Scans the storage directory and returns a list of all available audio assets."""
    if not os.path.exists(settings.SONGS_DIR):
        return []
    songs = [f for f in os.listdir(settings.SONGS_DIR) if f.endswith(".mp3")]
    return sorted(songs)