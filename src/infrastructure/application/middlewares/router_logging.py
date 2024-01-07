import structlog
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.stdlib.get_logger()


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        await logger.info(
            "Incoming request",
            extra={
                "req": {"method": request.method, "url": str(request.url)},
                "res": {
                    "status_code": response.status_code,
                },
            },
        )
        return response
