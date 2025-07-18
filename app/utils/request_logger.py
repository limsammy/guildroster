"""
Request logging middleware for GuildRoster.

Provides enhanced logging with frontend context information.
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request details with frontend context."""

    def __init__(self, app, include_headers: bool = True):
        super().__init__(app)
        self.include_headers = include_headers

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Extract context information
        user_agent = request.headers.get("user-agent", "Unknown")
        referer = request.headers.get("referer", "Unknown")
        frontend_route = request.headers.get("x-frontend-route", "Unknown")

        # Determine if this is a frontend request
        is_frontend = "GuildRoster-Frontend" in user_agent

        # Log request start
        log_message = f"Request: {request.method} {request.url.path}"
        if is_frontend:
            log_message += (
                f" | Frontend Route: {frontend_route} | Referer: {referer}"
            )

        logger.info(log_message)

        # Process the request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        status_code = response.status_code
        log_message = f"Response: {request.method} {request.url.path} -> {status_code} ({process_time:.3f}s)"
        if is_frontend:
            log_message += f" | Frontend Route: {frontend_route}"

        # Use different log levels based on status code
        if status_code >= 500:
            logger.error(log_message)
        elif status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        return response


def log_request_context(request: Request, message: str = ""):
    """
    Utility function to log request context from within route handlers.

    Args:
        request: FastAPI request object
        message: Additional message to include
    """
    user_agent = request.headers.get("user-agent", "Unknown")
    referer = request.headers.get("referer", "Unknown")
    frontend_route = request.headers.get("x-frontend-route", "Unknown")

    is_frontend = "GuildRoster-Frontend" in user_agent

    log_message = f"Route Context: {request.method} {request.url.path}"
    if message:
        log_message += f" | {message}"
    if is_frontend:
        log_message += (
            f" | Frontend Route: {frontend_route} | Referer: {referer}"
        )

    logger.info(log_message)
