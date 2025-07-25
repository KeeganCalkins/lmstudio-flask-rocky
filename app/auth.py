import os
from flask import request, jsonify, g, current_app
from functools import wraps
import jwt
from jwt import PyJWKClient
from loginUtils import db

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
JWKS_URL  = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"msg":"Missing token"}), 401
        token = auth.split()[1]
        
        try:
            jwk_client   = PyJWKClient(JWKS_URL)
            signing_key  = jwk_client.get_signing_key_from_jwt(token).key
            valid_issuers = [
                f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
                f"https://sts.windows.net/{TENANT_ID}/",
            ]
            #current_app.logger.info("Accepting issuers: %s", valid_issuers)
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=CLIENT_ID,
                options={ "verify_iss": False }
            )
            # manually enforce issuer
            iss = claims.get("iss")
            if iss not in valid_issuers:
                current_app.logger.error("Rejected token issuer: %s", iss)
                return jsonify({"msg":"Invalid token","error":"Invalid issuer"}), 401
            g.user_claims = claims
        except Exception as e:
            current_app.logger.error("JWT decode failed: %s", e)
            return jsonify({"msg":"Invalid token","error":str(e)}), 401
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        claims = getattr(g, "user_claims", None)
        if not claims or "oid" not in claims:
            return jsonify({"msg":"Missing authentication"}), 401
        
        oid = claims["oid"]
        user = db.users.find_one({ "azureOID": oid })
        
        if not user or not user.get("isAdmin", False):
            return jsonify({"msg":"Admin privileges required"}), 403
        
        g.current_user = user
        return f(*args, **kwargs)
    return wrapper