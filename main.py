from typing import Any, Dict
import logging
import time

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import RootModel
from merge import deep_merge
from starlette.exceptions import HTTPException as StarletteHTTPException


# Log Setup

logger = logging.getLogger("memory_service")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO) 


# App setup 

app = FastAPI(title="Memory Service", version="1.0.0")

STORE: Dict[str, Dict[str, Any]] = {}
ALLOWED_SLOTS = {"public", "private"}

def _get_slot(c_id: str) -> Dict[str, Any]:
    return STORE.setdefault(c_id, {"public": None, "private": None})

class JsonAny(RootModel[Any]):
    pass


# Middleware

@app.middleware("http")
async def access_log_and_correlation(request: Request, call_next):
    started = time.perf_counter()
    corr_id = request.headers.get("aplm-correlation-id")
    client_host = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path

    logger.info(
        f"REQ start method={method} path={path} ip={client_host} corr_id={corr_id}"
    )
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        logger.exception(
            f"REQ error method={method} path={path} ip={client_host} "
            f"corr_id={corr_id} duration_ms={duration_ms}: {exc}"
        )
        raise

    duration_ms = int((time.perf_counter() - started) * 1000)
    logger.info(
        f"REQ end   method={method} path={path} status={response.status_code} "
        f"ip={client_host} corr_id={corr_id} duration_ms={duration_ms}"
    )

    if corr_id:
        response.headers["aplm-correlation-id"] = corr_id
    return response


# Health Check

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}


# Error handlers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    corr_id = request.headers.get("aplm-correlation-id")
    logger.warning(
        f"422 validation_error path={request.url.path} corr_id={corr_id} errors={exc.errors()}"
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": exc.errors(),
                "correlation_id": corr_id,
            }
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    corr_id = request.headers.get("aplm-correlation-id")
    logger.warning(
        f"{exc.status_code} http_error path={request.url.path} corr_id={corr_id} detail={exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "http_error",
                "message": str(exc.detail),
                "correlation_id": corr_id,
            }
        },
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    corr_id = request.headers.get("aplm-correlation-id")
    logger.exception(
        f"500 internal_error path={request.url.path} corr_id={corr_id}: {exc}"
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred",
                "correlation_id": corr_id,
            }
        },
    )


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    corr_id = request.headers.get("aplm-correlation-id")
    logger.warning(
        f"{exc.status_code} http_error path={request.url.path} corr_id={corr_id} detail={exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "http_error",
                "message": str(exc.detail),
                "correlation_id": corr_id,
            }
        },
    )

# Helpers

def _ensure_valid_slot(slot_name: str):
    if slot_name not in ALLOWED_SLOTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid slot_name '{slot_name}'. Use 'public' or 'private'.",
        )


# Data Management

@app.get("/v1/conversations/{conversation_id}/{slot_name}-data")
def get_data(conversation_id: str, slot_name: str):
    _ensure_valid_slot(slot_name)
    value = _get_slot(conversation_id)[slot_name]
    logger.debug(f"GET {slot_name} cid={conversation_id} -> {value!r}")
    return value

@app.post("/v1/conversations/{conversation_id}/{slot_name}-data")
def post_data(conversation_id: str, slot_name: str, payload: JsonAny):
    _ensure_valid_slot(slot_name)
    slot = _get_slot(conversation_id)
    before = slot[slot_name]
    after = deep_merge(before, payload.root)
    slot[slot_name] = after
    logger.info(
        f"POST {slot_name} cid={conversation_id} merged "
        f"(before_type={type(before).__name__}, after_type={type(after).__name__})"
    )
    return after

@app.delete("/v1/conversations/{conversation_id}/{slot_name}-data", status_code=204)
def delete_data(conversation_id: str, slot_name: str):
    _ensure_valid_slot(slot_name)
    slot = _get_slot(conversation_id)
    slot[slot_name] = None
    logger.info(f"DELETE {slot_name} cid={conversation_id} -> set to null")