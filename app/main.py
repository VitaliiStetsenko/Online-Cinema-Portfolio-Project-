"""Main FastAPI application."""

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.cart import router as cart_router
from app.api.favorites import router as favorites_router
from app.api.interactions import router as interactions_router
from app.api.movies import catalog_router, router as movies_router
from app.api.users import router as users_router
from app.api.dependencies import get_current_active_user
from app.core.security import decode_token

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    debug=settings.debug,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(auth_router, prefix="/api")
app.include_router(cart_router, prefix="/api")
app.include_router(favorites_router, prefix="/api")
app.include_router(interactions_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(movies_router, prefix="/api")
app.include_router(catalog_router, prefix="/api")


@app.get("/docs", include_in_schema=False)
async def protected_swagger(access_token: str = Query(...)):
    """Show Swagger only to authenticated users."""
    if not decode_token(access_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid documentation token")
    return HTMLResponse("""<!doctype html><html><body><p>Opening protected Swagger UI...</p>
        <script>
          const token = new URLSearchParams(location.search).get('access_token');
          location.href = '/docs/ui?access_token=' + encodeURIComponent(token);
        </script></body></html>""")


@app.get("/docs/ui", include_in_schema=False)
async def swagger_ui(access_token: str = Query(...)):
    """Render Swagger UI which reads the token entered on the docs page."""
    if not decode_token(access_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid documentation token")
    return HTMLResponse(f"""<!doctype html><html><head>
        <link rel='stylesheet' href='https://unpkg.com/swagger-ui-dist@5/swagger-ui.css'>
        </head><body><div id='swagger-ui'></div>
        <script src='https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js'></script>
        <script>SwaggerUIBundle({{
          url:'/openapi.json', dom_id:'#swagger-ui', requestInterceptor:(request)=>{{
            request.headers.Authorization='Bearer {access_token}'; return request;
          }}
        }});</script></body></html>""")


@app.get("/openapi.json", include_in_schema=False)
async def protected_openapi(request: Request, _: object = Depends(get_current_active_user)):
    """Return OpenAPI schema only to authenticated users."""
    return JSONResponse(get_openapi(title=settings.app_title, version=settings.app_version, routes=app.routes))


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Online Cinema API"}
