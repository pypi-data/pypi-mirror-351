import logging
from typing import Optional, List, Dict, Any
import jwt
import requests
from functools import lru_cache

logger = logging.getLogger("supercortex.auth.utilities")


@lru_cache(maxsize=8)
def fetch_jwks(jwks_url: str) -> Dict[str, Any]:
    """
    Fetch and cache the JWKS (JSON Web Key Set) from a URL
    
    Args:
        jwks_url: URL to fetch the JWKS from
        
    Returns:
        Dictionary containing the JWKS (keys field contains the list of JWKs)
    """
    try:
        logger.debug(f"Fetching JWKS from {jwks_url}")
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        jwks = response.json()
        logger.debug(f"Successfully fetched JWKS containing {len(jwks.get('keys', []))} keys")
        return jwks
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {str(e)}")
        return {"keys": []}


def get_signing_key(jwks: Dict[str, Any], kid: Optional[str]) -> Optional[Any]:
    """
    Get the signing key from JWKS by Key ID
    
    Args:
        jwks: JWKS dictionary
        kid: Key ID to look for
        
    Returns:
        Signing key object if found, None otherwise
    """
    if not kid:
        logger.warning("No kid provided for key lookup")
        return None
        
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            try:
                signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                return signing_key
            except Exception as e:
                logger.error(f"Failed to parse JWK: {str(e)}")
                
    logger.warning(f"No matching key found for kid: {kid}")
    return None


def clear_jwks_cache():
    """Clear the JWKS cache to force a refresh on next fetch"""
    fetch_jwks.cache_clear()
    logger.debug("JWKS cache cleared")
    
    
def is_token_expired(token: str) -> bool:
    """
    Check if a JWT token is expired
    
    Args:
        token: JWT token to check
        
    Returns:
        True if token is expired, False otherwise
    """
    try:
        # Decode without verification, just to check expiration
        decoded = jwt.decode(token, options={"verify_signature": False})
        import time
        return decoded.get("exp", 0) < time.time()
    except jwt.ExpiredSignatureError:
        return True
    except Exception as e:
        logger.error(f"Error checking token expiration: {str(e)}")
        return True  # Assume expired if there's an error 