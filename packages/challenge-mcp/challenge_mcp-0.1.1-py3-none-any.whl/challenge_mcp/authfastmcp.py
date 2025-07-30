from mcp.server.fastmcp.server import FastMCP, lifespan_wrapper
from mcp.server.lowlevel.server import Server, LifespanResultT
from typing import Any
from mcp.server.session import ServerSession
from mcp.shared.session import RequestResponder
import mcp.types as types
from mcp.server.lowlevel.server import lifespan as default_lifespan
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging

logger = logging.getLogger(__name__)


class AuthTokenMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts bearer tokens from Authorization headers
    and stores them in the fastmcp for later access.
    """

    async def dispatch(self, request: Request, call_next):
        """Extract bearer token from headers."""
        logger.debug("AuthTokenMiddleware: Processing request")
        auth_header = request.headers.get("Authorization", "")
        logger.debug(
            f"AuthTokenMiddleware: Authorization header: {auth_header[:10]}..."
        )
        token = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            logger.debug(
                f"AuthTokenMiddleware: Extracted bearer token: {token[:10]}..."
            )
            request.app._parent._token = token

            logger.debug("AuthTokenMiddleware: Token stored in request.state and scope")
        else:
            logger.debug("AuthTokenMiddleware: No valid bearer token found in headers")

        response = await call_next(request)
        return response


class AuthServer(Server):
    """Extended FastMCP server that extracts and stores bearer tokens."""

    async def _handle_request(
        self,
        message: RequestResponder[types.ClientRequest, types.ServerResult],
        req: Any,
        session: ServerSession,
        lifespan_context: LifespanResultT,
        raise_exceptions: bool,
    ):
        """Extract bearer token from fastmcp and set in mcp session."""
        session.auth_token = self._parent._token

        # # Get the original response
        await super()._handle_request(
            message, req, session, lifespan_context, raise_exceptions
        )


class AuthFastMCP(FastMCP):

    def __init__(
        self, name: str | None = None, instructions: str | None = None, **settings: Any
    ):
        super().__init__(name, instructions, **settings)
        self._mcp_server = AuthServer(
            name=name or "FastMCP",
            instructions=instructions,
            lifespan=(
                lifespan_wrapper(self, self.settings.lifespan)
                if self.settings.lifespan
                else default_lifespan
            ),
        )
        self._mcp_server._parent = self
        self._setup_handlers()

    def sse_app(self, *args, **kwargs) -> Starlette:
        app = super().sse_app(*args, **kwargs)
        app._parent = self
        app.add_middleware(AuthTokenMiddleware)
        return app
