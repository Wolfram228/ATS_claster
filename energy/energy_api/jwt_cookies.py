from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

ACCESS_COOKIE = 'access'
REFRESH_COOKIE = 'refresh'
LOGGED_IN_COOKIE = 'logged_in'

def _cookie_flags():
    return {
        'secure': not settings.DEBUG,
        'samesite': 'Lax',
        'path': '/',
    }

def set_auth_cookies(response, access, refresh=None):
    flags = _cookie_flags()
    access_max_age = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
    refresh_max_age = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
    
    response.set_cookie(
        ACCESS_COOKIE,
        access,
        max_age=access_max_age,
        httponly=True,
        **flags,
    )
    
    if refresh:
        response.set_cookie(
            REFRESH_COOKIE,
            refresh,
            max_age=refresh_max_age,
            httponly=True,
            **flags,
        )
        response.set_cookie(
            LOGGED_IN_COOKIE,
            '1',
            max_age=refresh_max_age,
            httponly=False,
            **flags,
        )
    return response

def clear_auth_cookies(response):
    flags = _cookie_flags()
    for name in (ACCESS_COOKIE, REFRESH_COOKIE, LOGGED_IN_COOKIE):
        response.delete_cookie(name, path=flags['path'], samesite=flags['samesite'])
    return response


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            try:
                return super().authenticate(request)
            except (InvalidToken, TokenError, AuthenticationFailed):
                return None
                
        raw_token = request.COOKIES.get(ACCESS_COOKIE)
        if not raw_token:
            return None
            
        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, TokenError, AuthenticationFailed):
            return None
