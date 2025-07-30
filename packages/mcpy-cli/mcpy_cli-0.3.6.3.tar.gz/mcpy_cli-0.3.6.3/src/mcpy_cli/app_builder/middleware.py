"""
Middleware for session management in MCP applications.
"""

import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)

# Thread-local storage for session context
_session_context = threading.local()


class SSEDebugMiddleware:
    """
    Debug middleware specifically for SSE connections to help diagnose cloud environment issues.
    Logs detailed request/response information for MCP endpoints.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request_path = scope.get("path", "")
            request_method = scope.get("method", "")
            
            # Log ALL requests to see if POST /messages/ requests are reaching us
            headers = dict(scope.get("headers", []))
            client_info = scope.get("client", ("unknown", 0))
            
            # Decode headers for logging
            decoded_headers = {}
            for name, value in headers.items():
                try:
                    decoded_headers[name.decode("utf-8")] = value.decode("utf-8")
                except UnicodeDecodeError:
                    decoded_headers[name.decode("utf-8", errors="ignore")] = "<binary>"
            
            logger.info(f"SSE Debug: {request_method} {request_path} from {client_info[0]}:{client_info[1]}")
            
            # Only log detailed headers for MCP-related paths to avoid spam
            if "/mcp" in request_path or "/messages" in request_path:
                logger.info(f"SSE Debug: Headers: {decoded_headers}")
                
                # Wrap send to log response details
                async def debug_send(message):
                    if message["type"] == "http.response.start":
                        status = message.get("status", "unknown")
                        response_headers = message.get("headers", [])
                        decoded_response_headers = {}
                        for name, value in response_headers:
                            try:
                                decoded_response_headers[name.decode("utf-8")] = value.decode("utf-8")
                            except UnicodeDecodeError:
                                decoded_response_headers[name.decode("utf-8", errors="ignore")] = "<binary>"
                        
                        logger.info(f"SSE Debug: Response {status} for {request_path}")
                        logger.info(f"SSE Debug: Response headers: {decoded_response_headers}")
                    
                    await send(message)
                
                await self.app(scope, receive, debug_send)
            else:
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)


class SessionMiddleware:
    """
    Middleware to extract MCP session ID from request headers and store it in thread-local storage.
    This enables tools to access the current session ID during request processing.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Extract headers from the ASGI scope
            headers = dict(scope.get("headers", []))

            # Look for the mcp-session-id header (headers are byte strings in ASGI)
            session_id = None
            for name, value in headers.items():
                if name == b"mcp-session-id":
                    session_id = value.decode("utf-8")
                    break

            # If no session ID in headers, check query parameters as fallback
            if not session_id:
                query_string = scope.get("query_string", b"").decode("utf-8")
                if query_string:
                    from urllib.parse import parse_qs
                    query_params = parse_qs(query_string)
                    if "session_id" in query_params:
                        session_id = query_params["session_id"][0]

            # Enhanced logging for cloud debugging
            request_path = scope.get("path", "unknown")
            request_method = scope.get("method", "unknown")
            client_info = scope.get("client", ("unknown", 0))
            
            if session_id:
                # Set the session ID in thread-local storage
                set_current_session_id(session_id)
                logger.info(
                    f"SessionMiddleware: Set session ID {session_id} for {request_method} {request_path} from {client_info[0]}"
                )
            else:
                # Log all headers for debugging when session ID is missing
                header_names = [name.decode("utf-8", errors="ignore") for name, _ in headers.items()]
                query_string = scope.get("query_string", b"").decode("utf-8")
                logger.warning(
                    f"SessionMiddleware: No mcp-session-id header or session_id query param found for {request_method} {request_path} from {client_info[0]}. "
                    f"Available headers: {header_names}, Query: {query_string}"
                )

            try:
                # Process the request
                await self.app(scope, receive, send)
            finally:
                # Clean up thread-local storage after request processing
                if hasattr(_session_context, "session_id"):
                    delattr(_session_context, "session_id")
                    logger.debug(
                        f"SessionMiddleware: Cleaned up session ID from thread-local storage for {request_path}"
                    )
        else:
            # For non-HTTP requests (like WebSocket), just pass through
            logger.debug(f"SessionMiddleware: Passing through non-HTTP request: {scope.get('type', 'unknown')}")
            await self.app(scope, receive, send)


def get_current_session_id() -> Optional[str]:
    """
    Get the current session ID from thread-local storage.

    Returns:
        The session ID if available, None otherwise.
    """
    session_id = getattr(_session_context, "session_id", None)
    if session_id:
        logger.debug(f"Retrieved session ID from thread-local storage: {session_id}")
    else:
        logger.debug("No session ID found in thread-local storage")
    return session_id


def set_current_session_id(session_id: str) -> None:
    """
    Set the current session ID in thread-local storage.

    Args:
        session_id: The session ID to store.
    """
    logger.debug(f"Setting session ID in thread-local storage: {session_id}")
    _session_context.session_id = session_id
