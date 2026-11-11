from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

# ИЗМЕНЕНИЕ 1: Оставили только TokenVerifyView и импортировали свои классы из jwt_cookies
from rest_framework_simplejwt.views import TokenVerifyView
from energy_api.jwt_cookies import CookieTokenObtainPairView, CookieTokenRefreshView

from energy_api import views
from energy_api.views_auth import register, profile, logout, change_password
from django.conf import settings

from energy_api.api import EnergyApiViewSet

router = routers.DefaultRouter()
router.register(r'', EnergyApiViewSet, basename='regions-list')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    
    # ИЗМЕНЕНИЕ 2: Заменили стандартные View на Cookie-версии
    path('api/token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    # TokenVerifyView не трогаем
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    path('api/auth/register/', register, name='register'),
    path('api/auth/profile/', profile, name='profile'),
    path('api/auth/logout/', logout, name='logout'),
    path('api/auth/change-password/', change_password, name='change_password'),
    
    path('api/', include(router.urls)),
]

#if settings.DEBUG:
#    import debug_toolbar
#    urlpatterns = [
#        path('__debug__/', include(debug_toolbar.urls)),
#    ] + urlpatterns
