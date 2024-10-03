from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.api.routers.users import router as users_router
from app.api.routers.auth import router as auth_router
from app.api.security.authentication import JWTBearer
from app.service.errors import ServiceError

app = FastAPI()


# @app.get("/")
# def index():
#     return "Index"


@app.exception_handler(500)
def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(
            {"code": 500, "error_message": "Internal Server Error"}
        ),
    )


@app.exception_handler(ServiceError)
def service_error_handler(request: Request, exc: ServiceError):
    service_error_data = exc.__dict__()
    http_status_code = service_error_data.pop("http_code")
    return JSONResponse(
        status_code=http_status_code,
        content=jsonable_encoder(service_error_data),
    )


app.include_router(auth_router, tags=["authentication"])
app.include_router(users_router, tags=["users"], dependencies=[Depends(JWTBearer())])
