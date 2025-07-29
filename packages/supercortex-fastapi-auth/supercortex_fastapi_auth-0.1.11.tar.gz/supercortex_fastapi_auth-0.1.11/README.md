# SuperCortex Auth Libraries

This directory contains the client libraries for integrating with the SuperCortex Auth System.

## Libraries

### Python Library (`supercortex-fastapi-auth`)
- **Location**: `src/supercortex_fastapi_auth/`
- **Purpose**: Adds authentication support to FastAPI services
- **Features**: JWT validation, middleware, dependencies, protected routes

### React Library (`@supercortex/auth-client`)
- **Location**: `superocrtex-react-auth/`
- **Purpose**: Frontend integration with auth system
- **Features**: React hooks, auth context, API interceptors

## Quick Start

See the main [README.md](../README.md) for complete integration instructions.

### Python Library
```python
from supercortex_fastapi_auth import Auth

auth = Auth(auth_url="https://auth.apps.yourdomain.com")
auth.setup(app)
```

### React Library
```tsx
import { AuthProvider, useAuth } from '@supercortex/auth-client';

// Wrap your app
<AuthProvider>{children}</AuthProvider>

// Use in components
const { user, login, logout } = useAuth();
```

## Development

### Python Library
```bash
cd libraries
pip install -e .
```

### React Library
```bash
cd libraries/superocrtex-react-auth
npm install
npm run build
```

## Examples

See the `examples/` directory for complete usage examples.

## Documentation

For complete documentation, architecture details, and integration guides, see the main [README.md](../README.md). 