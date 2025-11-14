from django.contrib import admin
from django.urls import path, include
from energy_api import views
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('api/regions/', views.regions_list, name='regions'),
    path('api/table/', views.table_data, name='table'),
    path('api/summary/', views.summary_data, name='summary'),
    path('api/history/', views.load_history, name='history'),
    path('api/reload/', views.reload_data, name='reload'),
    path('api/report/xls/', views.download_report, name='report_xls'),
]

#if settings.DEBUG:
#    import debug_toolbar
#    urlpatterns = [
#        path('__debug__/', include(debug_toolbar.urls)),
#    ] + urlpatterns
