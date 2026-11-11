from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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
            return super().authenticate(request)
        raw_token = request.COOKIES.get(ACCESS_COOKIE)
        if not raw_token:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access = response.data.get('access')
            refresh = response.data.get('refresh')
            set_auth_cookies(response, access, refresh)
            response.data = {'detail': 'Login successful'}
        return response

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        data = {}
        if request.data:
            data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            
        if not data.get('refresh'):
            cookie_refresh = request.COOKIES.get(REFRESH_COOKIE)
            if cookie_refresh:
                data['refresh'] = cookie_refresh

        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            response = Response(
                {'detail': 'Invalid refresh token'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            clear_auth_cookies(response)
            return response

        access = str(serializer.validated_data['access'])
        refresh = serializer.validated_data.get('refresh')
        
        response = Response({'detail': 'Token refreshed'})
        if refresh:
            set_auth_cookies(response, access, str(refresh))
        else:
            set_auth_cookies(response, access)
            
        return response
