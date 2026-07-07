from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from app.config import settings

# Initialize Bcrypt context for secure, irreversible password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Converts a plain text password into a secure hash to save in the database."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares an inputted plain text password with the stored hash to check if they match."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Generates an encrypted JWT access token that keeps the user logged in."""
    to_encode = data.copy()
    
    # Calculate the expiration time (set to 24 hours from now)
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Sign and encrypt the token using our secret key
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt