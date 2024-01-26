from urllib.parse import parse_qs

import jwt
from django.conf import settings
from django.db import close_old_connections


class CustomTokenAuthMiddleware:
    """
    Custom auth token used in socket authentication
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode("utf-8")
        token_param = parse_qs(query_string).get("token", None)

        if token_param is None or not token_param:
            return None

        token = token_param[0]

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
        except jwt.ExpiredSignatureError:
            return None

        # Add the user_id to the scope
        scope["user_id"] = decoded_token["user_id"]

        close_old_connections()
        return await self.inner(scope, receive, send)
