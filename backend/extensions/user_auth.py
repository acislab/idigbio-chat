import flask
from flask import request, Flask
from keycloak import KeycloakOpenID


class UserAuth:
    token_issuer: str
    _kc: KeycloakOpenID

    def init_app(self, app: Flask, kc: KeycloakOpenID):
        self._kc = kc
        self.token_issuer = f"{kc.connection.base_url}/realms/{kc.realm_name}"

    def login(self, auth_code: str):
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
        self._kc.logout(refresh_token=None)

    def refresh_token(self, token: str):
        self._kc.refresh_token(token)
