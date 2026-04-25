from fastapi import Header, HTTPException
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET", "ustbite-jwt-secret-change-in-prod")
JWT_ALGORITHM = "HS256"


async def get_user_headers(
    authorization: str | None = Header(None),
    x_user_id: str | None = Header(None),
    x_user_email: str | None = Header(None),
) -> dict:
    """Extract user info from JWT Bearer token (primary) or legacy headers (fallback)."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "name": payload.get("name"),
            }
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    # Legacy fallback (internal service-to-service calls)
    if x_user_id:
        return {"user_id": x_user_id, "email": x_user_email, "name": None}

    return {"user_id": None, "email": None, "name": None}
