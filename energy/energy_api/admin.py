from django.contrib import admin
from .models import ElecReport, LoadHistory

@admin.register(ElecReport)
class ElecReportAdmin(admin.ModelAdmin):
    list_display = ['region', 'timestamp', 'plan_GES', 'plan_AES', 'price_buy']
    list_filter = ['region', 'timestamp']
    search_fields = ['region']
    date_hierarchy = 'timestamp'

@admin.register(LoadHistory)
class LoadHistoryAdmin(admin.ModelAdmin):
    list_display = ['data_date', 'load_time', 'count']
    list_filter = ['data_date']
    date_hierarchy = 'data_date'