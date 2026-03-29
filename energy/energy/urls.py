from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from energy_api import views
from energy_api.views_auth import register, profile, logout, change_password
from django.conf import settings

from energy_api.api import EnergyApiViewSet

router = routers.DefaultRouter()
router.register(r'', EnergyApiViewSet, basename='regions-list')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
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
