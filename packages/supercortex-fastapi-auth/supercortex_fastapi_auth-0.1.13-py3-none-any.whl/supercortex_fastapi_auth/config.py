from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AuthConfig:
    """Configuration for SuperCortex FastAPI Auth"""
    auth_url: str
    jwks_url: Optional[str] = None
    cookie_name: str = "auth_token"
    public_paths: List[str] = field(default_factory=lambda: ["/health", "/docs", "/openapi.json"])
    algorithm: str = "RS256"
    auth_header_name: str = "Authorization"
    auth_header_type: str = "Bearer"
    auth_enabled: bool = True 