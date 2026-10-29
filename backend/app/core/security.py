"""Get user id from the X-User-Id header, insecure but sufficient for this project.

TRIM: Authentication seam. NOT SECURE: this project deliberately has no real login.

Today the caller identifies itself with an `X-User-Id` header (a user picker in the UI). Anyone
can claim any identity. `get_current_user_id` is the ONE place to replace; every controller
receives the identity through app/dependencies.py:get_current_user, so nothing else changes.

Target design: OAuth2 / OpenID Connect (OAuth 2.1 direction) with an identity provider (IdP)
such as Keycloak, Auth0 or Entra ID. JWT is only the token format used by that flow. We do not
hand-roll password login.

  Browser (SPA)                         IdP                           This API (resource server)
  1. redirect to /authorize  ------->  login + consent               (Authorization Code + PKCE)
  2. code  <---------------------------
  3. POST /token (code + verifier) -->  access token (JWT, ~5-15 min) + refresh token
  4. GET /api/tasks  Authorization: Bearer <access token> ------------------------>
  5. validate, then handle

What this function would look like:

    bearer = HTTPBearer()

    def get_current_user_id(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
        claims = jwt.decode(                  # e.g. PyJWT with PyJWKClient (cached JWKS)
            creds.credentials,
            key=jwks_client.get_signing_key_from_jwt(creds.credentials).key,
            algorithms=["RS256"],             # pin algorithms; never accept "none"
            audience=settings.oauth_audience,
            issuer=settings.oauth_issuer,
        )                                     # also verifies exp / nbf
        return claims["sub"]                  # stable user id from the IdP

Then:
- `users` gains an `external_subject` column (the `sub` claim); users are created on first login.
- Check scopes/roles from claims for authorization (e.g. `tasks:write`).
- Frontend: authorization-code + PKCE (e.g. oidc-client-ts), tokens in memory only or, better,
  a backend-for-frontend holding an httpOnly, Secure, SameSite cookie.
  Never use localStorage (XSS attack). See the matching note in frontend/src/api/client.ts.
- HTTPS everywhere: TLS terminates at the edge (Nginx / Ingress); this API trusts
  X-Forwarded-Proto (uvicorn --proxy-headers). See README "Security and HTTPS".
- Add rate limiting on auth-related routes and CORS only for known origins if the SPA moves
  to a different origin.
"""

from typing import Annotated

from fastapi import Header, HTTPException, status


def get_current_user_id(
    x_user_id: Annotated[int | None, Header()] = None,
) -> int:
    """Get the current user id from the X-User-Id header.

    Returns:
        int: The current user id.

    Raises:
        HTTPException: If the X-User-Id header is missing.
    """

    if x_user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing X-User-Id header")
    return x_user_id
