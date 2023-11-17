import secrets
import bcrypt


# Get bcrypt hash of password
def hashpwd(password: str) -> str:
    return bcrypt.hashpw(str.encode(password), bcrypt.gensalt()).decode()


# Check bcrypt password hash
def checkpwd(password: str, bcrypt_hash: str | None) -> bool:
    if bcrypt_hash:
        return bcrypt.checkpw(str.encode(password), str.encode(bcrypt_hash))

    return False


# Genereate new random token
def new_token():
    return secrets.token_urlsafe(32)
