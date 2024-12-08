import os

import flask
import jose
import requests
from flask import request, Flask
from jose import jwt
from keycloak import KeycloakOpenID

from extensions.user_data import User, UserMeta


class AuthenticationError(Exception):
    pass


class UserAuth:
    _token_issuer: str
    _kc: KeycloakOpenID

    def init_app(self, app: Flask):
        if "KEYCLOAK" in app.config:
            kc_config = app.config["KEYCLOAK"]
            kc = KeycloakOpenID(
                server_url=kc_config["URL"],
                client_id=kc_config["CLIENT_ID"],
                realm_name=kc_config["REALM_NAME"],
                client_secret_key=os.getenv("KC_SECRET"),
            )

            self._kc = kc
            self._token_issuer = f"{kc.connection.base_url}/realms/{kc.realm_name}"

            url, realm = kc_config['URL'], kc_config["REALM_NAME"]
            self._certs_url = f"{url}/realms/{realm}/protocol/openid-connect/certs"
        else:
            self._kc = None

    def login(self, auth_code: str):
        if not self._kc:
            raise RuntimeError("Missing Keycloak")

        token = self._kc.token(
            grant_type="authorization_code",
            code=auth_code,
            redirect_uri=request.root_url,
        )
        userinfo = self._kc.userinfo(token["access_token"])

        flask.session["user"] = userinfo
        flask.session["token"] = token

        return userinfo

    def logout(self):
        if not self._kc:
            raise RuntimeError("Missing Keycloak")

        self._kc.logout(refresh_token=None)

    def refresh_token(self, token: str):
        if not self._kc:
            raise RuntimeError("Missing Keycloak")

        self._kc.refresh_token(token)

    def authenticate(self, token) -> User:
        if not self._kc:
            raise RuntimeError("Missing Keycloak")

        try:
            # Debugging
            # unverified_claims = jwt.get_unverified_claims(token)
            # expected_issuer = f"{KEYCLOAK_URL}/realms/{REALM_NAME}"
            # actual_issuer = unverified_claims.get("iss")
            # print(f"Expected issuer: {expected_issuer}")
            # print(f"Actual issuer: {actual_issuer}")

            # Get the unverified headers to find the key ID
            headers = jwt.get_unverified_headers(token)
            kid = headers.get("kid")

            # Get the full JWKS
            jwks = self._get_public_key()

            # Find the matching key in the JWKS
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == kid:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "n": key["n"],
                        "e": key["e"]
                    }
                    break

            if not rsa_key:
                raise AuthenticationError("Failed to find appropriate key")

            user_id, user_meta = self._read_user_token(token, rsa_key)
            return User(user_id, user_meta)

        except jose.ExpiredSignatureError as e:
            raise AuthenticationError("Expired token") from e
        except jose.JWTError as e:
            raise AuthenticationError("Invalid token") from e

    def _get_public_key(self):
        response = requests.get(self._certs_url)
        keys = response.json()
        # Return the complete key set - python-jose will handle key selection
        return keys

    def _read_user_token(token, rsa_key) -> (str, UserMeta):
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
            issuer=self._token_issuer
        )

        user_id = payload.get("sub")
        return (
            user_id,
            UserMeta(
                username=payload.get("preferred_username"),
                given_name=payload.get("preferred_username"),
                family_name=payload.get("family_name"),
                email=payload.get("email"),
                roles=payload.get("realm_access", {}).get("roles", [])
            )
        )
