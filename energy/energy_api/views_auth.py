from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

# Импортируем View из SimpleJWT
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Импортируем наши функции для куки
from energy_api.jwt_cookies import clear_auth_cookies, set_auth_cookies, REFRESH_COOKIE
from energy_api.models import UserProfile


# ==========================================
# НОВЫЕ КЛАССЫ ДЛЯ ЛОГИНА И ОБНОВЛЕНИЯ ТОКЕНА
# ==========================================

class CookieTokenObtainPairView(TokenObtainPairView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access = response.data.get('access')
            refresh = response.data.get('refresh')
            set_auth_cookies(response, access, refresh)
            response.data = {'detail': 'Login successful'}
        return response


class CookieTokenRefreshView(TokenRefreshView):
    authentication_classes = []
    permission_classes = [AllowAny]

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


# ==========================================
# ОСТАЛЬНЫЕ ФУНКЦИИ (БЕЗ ИЗМЕНЕНИЙ)
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    
    if not username or not password:
        return Response({
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({
            'error': 'User already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, password=password, email=email)
    UserProfile.objects.create(user=user)
    
    refresh = RefreshToken.for_user(user)
    
    response = Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    }, status=status.HTTP_201_CREATED)
    
    set_auth_cookies(response, str(refresh.access_token), str(refresh))
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'date_joined': user.date_joined,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    refresh_token = request.COOKIES.get(REFRESH_COOKIE) or request.data.get('refresh')
    response = Response({'message': 'Logout successful'})
    clear_auth_cookies(response)
    
    if not refresh_token:
        return response
        
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        pass
        
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return Response({
            'error': 'Old and new password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.check_password(old_password):
        return Response({
            'error': 'Wrong old password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    
    return Response({
        'message': 'Password changed successfully'
    })
