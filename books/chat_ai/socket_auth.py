import jwt
from urllib.parse import parse_qs
from account.models import User
from channels.db import database_sync_to_async
from django.conf import settings
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth.models import AnonymousUser



@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get("query_string", b"").decode())
        token = (query.get("token") or [None])[0]

        scope["user"] = AnonymousUser()

        if token:
            try:
                # Validate signature/expiry
                UntypedToken(token)
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = await get_user(payload.get("user_id"))
                
                scope["user"] = user
            except Exception:
                pass

        return await self.inner(scope, receive, send)
