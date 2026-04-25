from fastapi import Header, Request, HTTPException
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET", "ustbite-jwt-secret-change-in-prod")
JWT_ALGORITHM = "HS256"


async def get_trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", "")


async def get_user_headers(
    authorization: str | None = Header(None),
    # Also support legacy X-User-* headers from gateway injection (future)
    x_user_id: str | None = Header(None),
    x_user_email: str | None = Header(None),
) -> dict:
    """
    Extract user identity from either:
    1. JWT Bearer token in Authorization header (current approach)
    2. X-User-Email / X-User-Id headers (future gateway injection approach)
    """
    # Prefer JWT Bearer token
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "employee_id": payload.get("employee_id"),
            }
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired — please login again")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

    # Fallback: gateway-injected headers (for future OIDC proxy setup)
    if x_user_email:
        return {"user_id": x_user_id, "email": x_user_email, "employee_id": None}

    # No auth provided — endpoints that call this will return 401
    return {"user_id": None, "email": None, "employee_id": None}
