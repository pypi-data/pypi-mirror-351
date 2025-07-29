from fastapi import FastAPI, Depends, Request, HTTPException, APIRouter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send
from functools import wraps
import logging
import jwt
import httpx
import json
from typing import Dict, Any, Optional, List, Union, Callable
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import time

from .config import AuthConfig

logger = logging.getLogger("supercortex.auth")


class ASGIAuthMiddleware:
    """ASGI Middleware for authentication - higher performance than BaseHTTPMiddleware"""
    
    def __init__(self, app: ASGIApp, auth_instance):
        self.app = app
        self.auth = auth_instance
        
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        # Get path from scope
        path = scope.get("path", "")
        
        # Skip auth for public paths
        if self.auth._is_public_path(path):
            await self.app(scope, receive, send)
            return
            
        # TODO: Implement token extraction and validation at the ASGI level
        # This is more complex but offers better performance
        # For now, we'll defer this to the BaseHTTPMiddleware
        
        # Continue with request
        await self.app(scope, receive, send)


class Auth:
    """Authentication manager for FastAPI applications"""
    
    def __init__(self, auth_url: Union[str, AuthConfig], **kwargs):
        """Initialize with configuration
        
        Args:
            auth_url: Either the authentication service URL as a string or a complete AuthConfig object
            **kwargs: Additional configuration parameters if auth_url is a string
        """
        self.config = AuthConfig(auth_url=auth_url, **kwargs) if not isinstance(auth_url, AuthConfig) else auth_url
        self._jwks_cache = None
        self._jwks_cache_time = 0
        self._jwks_cache_ttl = 3600  # 1 hour cache
        logger.info(f"Auth initialized with auth_url={self.config.auth_url}, cookie_name={self.config.cookie_name}")
    
    def setup(self, app: FastAPI):
        """Set up authentication for the FastAPI application
        
        This method:
        1. Adds the authentication middleware to intercept requests
        2. Registers exception handlers for auth-related errors
        3. Adds required endpoints for frontend integration
        
        Args:
            app: The FastAPI application to configure
        """
        if not self.config.auth_enabled:
            logger.warning("Auth is disabled, setup will not add middleware")
            return
            
        # Register middleware - use BaseHTTPMiddleware for now
        # BaseHTTPMiddleware is easier to work with but has performance overhead
        app.add_middleware(BaseHTTPMiddleware, dispatch=self._auth_middleware)
        
        # TODO: Consider replacing with ASGI middleware for better performance
        # app.add_middleware(ASGIAuthMiddleware, auth_instance=self)
        
        # Register auth URL endpoint for frontend use
        @app.get("/api/v1/auth-url", tags=["auth"])
        async def get_auth_url():
            """Get the URL for authentication"""
            return {"login_url": f"{self.config.auth_url}/api/v1/auth/redirect"}
        
        # Register user endpoint that proxies to auth service
        @app.get("/api/v1/user", tags=["auth"])
        async def get_current_user_proxy(request: Request):
            """Get current user - proxies to auth service if token is valid"""
            if not self.config.auth_enabled:
                return {"sub": "mock-user", "email": "mock@example.com", "name": "Mock User"}
            
            user = getattr(request.state, "user", None)
            if not user:
                # Try to get user from auth service directly
                token = self._get_token(request)
                if token:
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.get(
                                f"{self.config.auth_url}/api/v1/auth/user",
                                cookies={self.config.cookie_name: token},
                                timeout=10.0
                            )
                            if response.status_code == 200:
                                return response.json()
                    except Exception as e:
                        logger.warning(f"Failed to fetch user from auth service: {e}")
                
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required",
                    headers={"login_url": f"{self.config.auth_url}/api/v1/auth/redirect"}
                )
            return user
        
        logger.info(f"Auth setup complete for FastAPI application")
    
    async def _auth_middleware(self, request: Request, call_next):
        """Internal middleware implementation
        
        This middleware:
        1. Checks if the path is public, skipping auth if it is
        2. Extracts the user from the request if present
        3. Attaches the user to request.state for later use
        4. Continues the request processing
        
        Auth enforcement happens in the dependencies, not here.
        """
        # Check if path is public
        if self._is_public_path(request.url.path):
            return await call_next(request)
            
        # Extract user and attach to request.state if present
        token = self._get_token(request)
        if token:
            try:
                # Validate token
                user = await self._validate_token(token)
                # Attach to request state for later use
                request.state.user = user
                logger.debug(f"User {user.get('email', user.get('sub', 'unknown'))} authenticated")
            except Exception as e:
                logger.warning(f"Invalid auth token: {str(e)}")
                # Invalid token, but don't block here
                pass
        
        # Continue processing the request
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        """Check if path should bypass authentication"""
        return any(path.startswith(prefix) for prefix in self.config.public_paths)
    
    def _get_token(self, request: Request) -> Optional[str]:
        """Extract token from request (cookie or header)"""
        # Try cookie first
        token = request.cookies.get(self.config.cookie_name)
        
        # If no cookie, try header
        if not token and self.config.auth_header_name in request.headers:
            auth = request.headers[self.config.auth_header_name]
            header_type = f"{self.config.auth_header_type} "
            if auth.startswith(header_type):
                token = auth.replace(header_type, "")
                
        return token
    
    async def _get_jwks(self) -> Dict[str, Any]:
        """Get JWKS from auth service with caching"""
        current_time = time.time()
        
        # Check if cache is still valid
        if (self._jwks_cache and 
            current_time - self._jwks_cache_time < self._jwks_cache_ttl):
            return self._jwks_cache
        
        # Fetch fresh JWKS
        try:
            jwks_url = self.config.jwks_url or f"{self.config.auth_url}/api/v1/auth/.well-known/jwks.json"
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_url, timeout=10.0)
                response.raise_for_status()
                jwks = response.json()
                
                # Cache the result
                self._jwks_cache = jwks
                self._jwks_cache_time = current_time
                
                return jwks
        except Exception as e:
            logger.error(f"Failed to fetch JWKS from {jwks_url}: {e}")
            # Return cached version if available, even if expired
            if self._jwks_cache:
                logger.warning("Using expired JWKS cache due to fetch failure")
                return self._jwks_cache
            raise

    async def _validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return user data"""
        try:
            # First decode without verification to get the header
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')
            
            if not kid:
                raise ValueError("Token missing 'kid' in header")
            
            # Get JWKS and find the matching key
            jwks = await self._get_jwks()
            
            # Find the key with matching kid
            key_data = None
            for key in jwks.get('keys', []):
                if key.get('kid') == kid:
                    key_data = key
                    break
            
            if not key_data:
                raise ValueError(f"No key found for kid: {kid}")
            
            # Convert JWK to PEM format for PyJWT
            if key_data.get('kty') == 'RSA':
                # Construct RSA public key from JWK
                from jwt.algorithms import RSAAlgorithm
                public_key = RSAAlgorithm.from_jwk(json.dumps(key_data))
            else:
                raise ValueError(f"Unsupported key type: {key_data.get('kty')}")
            
            # Verify and decode the token
            decoded = jwt.decode(
                token,
                public_key,
                algorithms=[self.config.algorithm],
                options={"verify_exp": True, "verify_aud": False}  # Skip audience verification for now
            )
            
            return decoded
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            raise HTTPException(status_code=401, detail="Token validation failed")
    
    async def required(self, request: Request) -> Dict[str, Any]:
        """Dependency for requiring authentication
        
        Returns the user if authenticated, raises 401 otherwise
        
        Usage:
            @app.get("/protected")
            async def protected_route(user = Depends(auth.required)):
                return {"message": f"Hello, {user['email']}"}
        """
        if not self.config.auth_enabled:
            # If auth is disabled, return a dummy user
            return {"sub": "mock-user", "email": "mock@example.com", "name": "Mock User"}
            
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(
                status_code=401, 
                detail="Authentication required",
                headers={
                    "WWW-Authenticate": f"Bearer",
                    "login_url": f"{self.config.auth_url}/api/v1/auth/redirect"
                }
            )
        return user
    
    async def optional(self, request: Request) -> Optional[Dict[str, Any]]:
        """Dependency for optional authentication
        
        Returns the user if authenticated, None otherwise
        
        Usage:
            @app.get("/public")
            async def public_route(user = Depends(auth.optional)):
                if user:
                    return {"message": f"Hello, {user['email']}"}
                return {"message": "Hello, anonymous user"}
        """
        if not self.config.auth_enabled:
            # If auth is disabled, return a dummy user
            return {"sub": "mock-user", "email": "mock@example.com", "name": "Mock User"}
            
        return getattr(request.state, "user", None)
    
    def router(self, prefix: str = "", tags: Optional[List[str]] = None) -> APIRouter:
        """Create a router with authentication required for all routes
        
        Args:
            prefix: URL prefix for all routes in this router
            tags: OpenAPI tags for documentation - helps group endpoints
                  in the Swagger UI documentation
                  
        Returns:
            An APIRouter with authentication required for all routes
            
        Usage:
            admin_router = auth.router("/admin", tags=["admin"])
            app.include_router(admin_router)
            
            @admin_router.get("/dashboard")
            async def admin_dashboard():
                return {"message": "Admin dashboard"}
        """
        if not self.config.auth_enabled:
            return APIRouter(prefix=prefix, tags=tags or [])
            
        return APIRouter(
            prefix=prefix,
            tags=tags or [],
            dependencies=[Depends(self.required)]
        )
        
    def required_decorator(self) -> Callable:
        """Decorator to require authentication for an endpoint
        
        Usage:
            @app.get("/protected")
            @auth.required_decorator()
            async def protected_route():
                return {"message": "Protected content"}
        """
        def decorator(func: Callable) -> Callable:
            if not self.config.auth_enabled:
                return func
                
            # Apply the dependency to the route
            dependencies = getattr(func, "dependencies", [])
            dependencies.append(Depends(self.required))
            func.dependencies = dependencies
            return func
        return decorator 