from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    """Hashes a plain text password using bcrypt."""
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    """Verifies a plain text password against its bcrypt hash."""
    return pwd_context.verify(plain, hashed)

