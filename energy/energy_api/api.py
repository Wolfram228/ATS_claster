import json
import subprocess
import os
import pandas as pd

from django.core.paginator import Paginator
from datetime import timedelta, datetime
from io import BytesIO
from django.db import connection
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse, FileResponse
from django.db.models import Q, Sum, Avg
from django.utils import timezone
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from energy_api.models import ElecReport, LoadHistory
from energy_api.serializers import ElecReportSerializer, LoadHistorySerializer


class EnergyApiViewSet(GenericViewSet):
    queryset = ElecReport.objects.all()
    serializer_class = ElecReportSerializer

    @action(methods=['GET'], url_path="check-login", detail=False)
    def check_login(self, request, *args, **kwargs):
        """Проверка статуса авторизации пользователя"""
        data = {
            'csrf': get_token(self.request),
            'isAuthenticated': bool(self.request.user.is_authenticated),
        }

        if self.request.user.is_authenticated:
            data.update({
                'username': self.request.user.username
            })

        return Response({
            'status': 'success',
            'data': data,
            'message': 'Login status retrieved successfully'
        })

    @action(methods=['GET'], url_path="regions", detail=False)
    def get_region_list(self, request, *args, **kwargs):
        """Список всех регионов"""
        cache_key = 'regions_list'
        regions = cache.get(cache_key)

        if regions is None:
            regions = list(ElecReport.objects.values_list('region', flat=True).distinct())
            cache.set(cache_key, regions, 3600)

        return Response({
            'status': 'success',
            'data': regions,
            'count': len(regions),
            'message': 'Regions list retrieved successfully'
        })

    @action(methods=['GET'], url_path='table-data', detail=False)
    def get_table_data(self, request, *args, **kwargs):
        """Табличные данные с фильтрацией"""
        date_from = request.GET.get('from')
        date_to = request.GET.get('to')
        region = request.GET.get('region')
        hour = request.GET.get('hour')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10000))

        """Валидация параметров"""
        if not date_from or not date_to:
            return Response({
                'status': 'error',
                'message': 'Оба параметра from и to обязательны'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            if 'T' in date_from:
                start_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            else:
                start_date = datetime.fromisoformat(date_from)
                end_date = datetime.fromisoformat(date_to)
        except ValueError:
            return Response({
                'status': 'error',
                'message': 'Неверный формат даты. Используйте YYYY-MM-DD или YYYY-MM-DDTHH:MM'
            }, status=status.HTTP_400_BAD_REQUEST)

        if end_date < start_date:
            return Response({
                'status': 'error',
                'message': 'to должно быть >= from'
            }, status=status.HTTP_400_BAD_REQUEST)

        max_days = 365 * 3
        if (end_date - start_date) > timedelta(days=max_days):
            return Response({
                'status': 'error',
                'message': 'Нельзя запрашивать больше чем 1200 дней'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        sql = """
        SELECT 
            *
        FROM elec_reports
        WHERE timestamp BETWEEN %s AND %s
        """

        params = [start_date.date(), end_date.date()]

        if region:
            sql += " AND region = %s"
            params.append(region)
    
        if hour:
            sql += " AND hour = %s"
            params.append(hour)

        sql += " ORDER BY timestamp, region"

        offset = (page - 1) * page_size
        sql += " LIMIT %s OFFSET %s"
        params.extend([page_size, offset])

        count_sql = """
        SELECT COUNT(*) 
        FROM elec_reports
        WHERE timestamp >= %s AND timestamp <= %s
        """
        count_params = [start_date.date(), end_date.date()]

        if region:
            count_sql += " AND region = %s"
            count_params.append(region)
    
        if hour:
            count_sql += " AND hour = %s"
            count_params.append(hour)
    
        with connection.cursor() as cursor:
            cursor.execute(count_sql, count_params)
            total_count = cursor.fetchone()[0]
            
            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
    
        data = []
        for row in rows:
            row_dict = dict(zip(columns, row))
        
            if 'timestamp' in row_dict and isinstance(row_dict['timestamp'], datetime):
                row_dict['timestamp'] = row_dict['timestamp'].isoformat()
        
            data.append(row_dict)
        
        return Response({
        'status': 'success',
        'data': data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'total_pages': (total_count + page_size - 1) // page_size,
            'has_next': page * page_size < total_count,
            'has_previous': page > 1
        },
        'count': len(data),
        'filters': {
            'date_from': date_from,
            'date_to': date_to,
            'region': region,
            'hour': hour
        },
        'message': f'Retrieved {len(data)} records (page {page} of {(total_count + page_size - 1) // page_size})'
	})

    @action(methods=['GET'], url_path='summary', detail=False)
    def get_summary_data(self, request, *args, **kwargs):
        """Сводные данные по объему и ценам"""
        date_from = request.GET.get('from')
        date_to = request.GET.get('to')
        region = request.GET.get('region')
        hour = request.GET.get('hour')

        if not date_from or not date_to:
            return Response({
                'status': 'error',
                'message': 'Оба параметра from и to обязательны'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            if 'T' in date_from:
                start_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            else:
                start_date = datetime.fromisoformat(date_from)
                end_date = datetime.fromisoformat(date_to)
        except ValueError:
            return Response({
                'status': 'error',
                'message': 'Неверный формат даты'
            }, status=status.HTTP_400_BAD_REQUEST)

        """Ключ для кэша"""
        cache_key = f"summary_{date_from}_{date_to}_{region}_{hour}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response({
                'status': 'success',
                'data': cached_data,
                'cached': True,
                'message': 'Summary data retrieved from cache'
            })

        """Базовый запрос"""
        queryset = ElecReport.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        if region:
            queryset = queryset.filter(region=region)
        
        if hour:
            queryset = queryset.filter(hour=hour)

        """Агрегация данных"""
        summary_data = queryset.values(
            'timestamp', 'hour'
        ).annotate(
            total_volume=Sum('plan_GES') + Sum('plan_AES') + Sum('plan_TES') + 
                        Sum('plan_SES') + Sum('plan_VES') + Sum('plan_other'),
            avg_price=Avg('price_buy')
        ).order_by('timestamp', 'hour')
        
        result = []
        for data in summary_data:
            full_timestamp = datetime.combine(
                data['timestamp'], 
                datetime.min.time()
            ).replace(hour=data['hour'])
            
            result.append({
                'timestamp': full_timestamp.isoformat(),
                'volume': round(data['total_volume'] or 0, 2),
                'price': round(data['avg_price'], 2) if data['avg_price'] else None
            })
        
        """Кэшируем на 5 минут"""
        cache.set(cache_key, result, 300)
        
        return Response({
            'status': 'success',
            'data': result,
            'count': len(result),
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
                'region': region,
                'hour': hour
            },
            'message': f'Retrieved {len(result)} summary records'
        })

    @action(methods=['GET'], url_path='load-history', detail=False)
    def get_load_history(self, request, *args, **kwargs):
        """История загрузки данных"""
        cache_key = 'load_history'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response({
                'status': 'success',
                'data': cached_data,
                'cached': True,
                'message': 'Load history retrieved from cache'
            })
        
        history = LoadHistory.objects.all().order_by('-data_date')[:50]
        serializer = LoadHistorySerializer(history, many=True)
        
        response_data = serializer.data
        
        """Кэшируем на 2 минуты"""
        cache.set(cache_key, response_data, 120)
        
        return Response({
            'status': 'success',
            'data': response_data,
            'count': len(response_data),
            'message': f'Retrieved {len(response_data)} history records'
        })

    @action(methods=['GET'], url_path='download-report', detail=False)
    def download_report(self, request, *args, **kwargs):
        """Скачать Excel отчет"""
        date_from = request.GET.get('from')
        date_to = request.GET.get('to')
        region = request.GET.get('region')
        hour = request.GET.get('hour')

        if not date_from or not date_to:
            return Response({
                'status': 'error',
                'message': 'Оба параметра from и to обязательны'
            }, status=status.HTTP_400_BAD_REQUEST)

        """Исправляем формат даты"""
        try:
            if 'T' in date_from:
                start_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            else:
                start_date = datetime.fromisoformat(date_from)
                end_date = datetime.fromisoformat(date_to)
        except ValueError:
            return Response({
                'status': 'error',
                'message': 'Неверный формат даты'
            }, status=status.HTTP_400_BAD_REQUEST)

        """Фильтрация данных с ограничением"""
        queryset = ElecReport.objects.filter(
            timestamp__gte=start_date.date(),
            timestamp__lte=end_date.date()
        )[:50000]
        
        if region:
            queryset = queryset.filter(region=region)
        
        if hour:
            queryset = queryset.filter(timestamp__hour=hour)

        """Подготовка данных для Excel"""
        data = []
        for record in queryset:
            row = {
                'Дата': record.timestamp.strftime('%Y-%m-%d'),
                'Регион': record.region,
                'Час': record.hour
            }
            
            fields = [
                'plan_GES', 'plan_AES', 'plan_TES', 'plan_SES', 'plan_VES', 'plan_other',
                'techmin_GES', 'techmin_AES', 'techmin_TES', 'techmin_SES', 'techmin_VES', 'techmin_other',
                'technomin_GES', 'technomin_AES', 'technomin_TES', 'technomin_SES', 'technomin_VES', 'technomin_other',
                'techmax_GES', 'techmax_AES', 'techmax_TES', 'techmax_SES', 'techmax_VES', 'techmax_other',
                'plan_consumption', 'plan_export', 'plan_import',
                'price_buy', 'price_sell', 'full_plan'
            ]
            
            for field in fields:
                value = getattr(record, field)
                row[field] = value if value is not None else 0
            
            data.append(row)
        
        """Создание Excel файла"""
        if not data:
            return Response({
                'status': 'error',
                'message': 'Нет данных для выбранного периода'
            }, status=status.HTTP_404_NOT_FOUND)
            
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        
        output.seek(0)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="energy_report.xlsx"'
        
        return response

