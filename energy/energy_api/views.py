import pandas as pd
import json
from io import BytesIO
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.db.models import Q, Sum, Avg
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ElecReport, LoadHistory
from .serializers import ElecReportSerializer, LoadHistorySerializer
from django.shortcuts import render
from datetime import datetime, timedelta, date
from django.db.models import Sum, Avg
from django.utils import timezone

@cache_page(60 * 5)
def index(request):

    today = date.today()
    yesterday = today - timedelta(days=1)
    day_before = yesterday - timedelta(days=1)
    
    gens = [
        ('plan_GES', 'ГЭС'),
        ('plan_AES', 'АЭС'), 
        ('plan_TES', 'ТЭС'),
        ('plan_SES', 'СЭС'),
        ('plan_VES', 'ВЭС'),
        ('plan_other', 'прочие ВИЭ')
    ]
    
    # Ключ для кэша с учетом региона
    region = request.GET.get('region', '')
    cache_key = f"index_data_{yesterday}_{region}"
    
    # Пробуем взять данные из кэша
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'index.html', cached_data)
    

    dates = [day_before, yesterday]
    
    # Получаем агрегированные данные за оба дня одним запросом
    hour_data = ElecReport.objects.filter(
        timestamp__date__in=dates
    ).values(
        'timestamp__date', 'timestamp__hour'
    ).annotate(
        **{f'sum_{key}': Sum(key) for key, _ in gens}
    ).order_by('timestamp__date', 'timestamp__hour')
    
    # Инициализация структур
    vol_prev = {key: [0]*24 for key, _ in gens}
    vol_yest = {key: [0]*24 for key, _ in gens}
    
 
    for data in hour_data:
        date_type = vol_prev if data['timestamp__date'] == day_before else vol_yest
        hour = data['timestamp__hour']
        
        for key, _ in gens:
            sum_field = f'sum_{key}'
            if sum_field in data and data[sum_field]:
                date_type[key][hour] = float(data[sum_field])
    

    shares_row = ElecReport.objects.filter(
        timestamp__date=yesterday
    ).aggregate(
        **{key: Sum(key) for key, _ in gens}
    )
    
    shares = {label: float(shares_row[key] or 0) for key, label in gens}
    

    prices_cache_key = f"prices_{region}_{today}"
    prices = cache.get(prices_cache_key)
    
    if prices is None:
        start_month = timezone.make_aware(datetime.combine(
            today - timedelta(days=31), 
            datetime.min.time()
        ))
        end_month = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        
        price_query = ElecReport.objects.filter(
            timestamp__gte=start_month,
            timestamp__lt=end_month
        )
        
        if region:
            price_query = price_query.filter(region=region)
        
        price_data = price_query.values('timestamp__date').annotate(
            avg_price=Avg('price_buy')
        ).order_by('timestamp__date')
        
        prices = [
            (data['timestamp__date'].strftime('%Y-%m-%d'), 
             round(data['avg_price'], 2) if data['avg_price'] else None)
            for data in price_data
        ]
        cache.set(prices_cache_key, prices, 3600)
    
    # Преобразуем в JSON-совместимые структуры
    context = {
        'gens_labels': json.dumps([label for _, label in gens]),
        'prev_date': day_before.strftime('%Y-%m-%d'),
        'yest_date': yesterday.strftime('%Y-%m-%d'),
        'vol_prev': json.dumps([vol_prev[key] for key, _ in gens]),
        'vol_yest': json.dumps([vol_yest[key] for key, _ in gens]),
        'shares': json.dumps(shares),
        'prices': json.dumps(prices),
        'region': region,
    }
    
    # Кэшируем данные на 5 минут
    cache.set(cache_key, context, 300)
    
    return render(request, 'index.html', context)
#   return HttpResposne(data=context, status=status.STATUS_200_OK)

@api_view(['GET'])
def regions_list(request):
    """Список всех регионов"""
    # Кэшируем список регионов на 1 час
    cache_key = 'regions_list'
    regions = cache.get(cache_key)
    
    if regions is None:
        regions = list(ElecReport.objects.values_list('region', flat=True).distinct())
        cache.set(cache_key, regions, 3600)
    
    return Response(regions)

@api_view(['GET'])
def table_data(request):
    """Табличные данные с фильтрацией"""
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    region = request.GET.get('region')
    hour = request.GET.get('hour')

    # Валидация параметров
    if not date_from or not date_to:
        return Response({'error': 'Оба параметра from и to обязательны'}, status=400)
    
    try:
        # Исправляем формат даты
        if 'T' in date_from:
            start_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        else:
            start_date = datetime.fromisoformat(date_from)
            end_date = datetime.fromisoformat(date_to)
    except ValueError:
        return Response({'error': 'Неверный формат даты. Используйте YYYY-MM-DD или YYYY-MM-DDTHH:MM'}, status=400)
    
    if end_date < start_date:
        return Response({'error': 'to должно быть >= from'}, status=400)
    
    if (end_date - start_date) > timedelta(days=365):
        return Response({'error': 'Нельзя запрашивать больше чем 365 дней'}, status=400)

    # Фильтрация данных
    queryset = ElecReport.objects.filter(
        timestamp__date__gte=start_date.date(),
        timestamp__date__lte=end_date.date()
    )
    
    if region:
        queryset = queryset.filter(region=region)
    
    if hour:
        queryset = queryset.filter(timestamp__hour=hour)

    # Ограничиваем количество записей для предотвращения перегрузки
    queryset = queryset.order_by('timestamp', 'region')[:10000]

    # Сериализация данных
    serializer = ElecReportSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def summary_data(request):
    """Сводные данные по объему и ценам"""
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    region = request.GET.get('region')
    hour = request.GET.get('hour')

    if not date_from or not date_to:
        return Response({'error': 'Оба параметра from и to обязательны'}, status=400)

    # Исправляем формат даты
    try:
        if 'T' in date_from:
            start_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        else:
            start_date = datetime.fromisoformat(date_from)
            end_date = datetime.fromisoformat(date_to)
    except ValueError:
        return Response({'error': 'Неверный формат даты'}, status=400)

    # Ключ для кэша
    cache_key = f"summary_{date_from}_{date_to}_{region}_{hour}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return Response(cached_data)

    # Базовый запрос
    queryset = ElecReport.objects.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date
    )
    
    if region:
        queryset = queryset.filter(region=region)
    
    if hour:
        queryset = queryset.filter(timestamp__hour=hour)

    # ОПТИМИЗАЦИЯ: Используем агрегацию БД вместо обработки в Python
    summary_data = queryset.values(
        'timestamp__date', 'timestamp__hour'
    ).annotate(
        total_volume=Sum('plan_GES') + Sum('plan_AES') + Sum('plan_TES') + 
                    Sum('plan_SES') + Sum('plan_VES') + Sum('plan_other'),
        avg_price=Avg('price_buy')
    ).order_by('timestamp__date', 'timestamp__hour')
    
    result = []
    for data in summary_data:
        full_timestamp = datetime.combine(
            data['timestamp__date'], 
            datetime.min.time()
        ).replace(hour=data['timestamp__hour'])
        
        result.append({
            'timestamp': full_timestamp.isoformat(),
            'volume': round(data['total_volume'] or 0, 2),
            'price': round(data['avg_price'], 2) if data['avg_price'] else None
        })
    
    # Кэшируем на 5 минут
    cache.set(cache_key, result, 300)
    
    return Response(result)

@api_view(['GET'])
def load_history(request):
    """История загрузки данных"""
    cache_key = 'load_history'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return Response(cached_data)
    
    history = LoadHistory.objects.all().order_by('-data_date')[:50]  # Ограничиваем количество
    serializer = LoadHistorySerializer(history, many=True)
    
    # Кэшируем на 2 минуты
    cache.set(cache_key, serializer.data, 120)
    
    return Response(serializer.data)

@api_view(['POST'])
def reload_data(request):
    """Запуск обновления данных"""
    from .management.commands.fetch_data import Command
    try:
        # Очищаем кэш при обновлении данных
        cache.clear()
        
        command = Command()
        command.handle()
        return Response({'status': 'success', 'message': 'Данные успешно обновлены'})
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def download_report(request):
    """Скачать Excel отчет"""
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    region = request.GET.get('region')
    hour = request.GET.get('hour')

    if not date_from or not date_to:
        return Response({'error': 'Оба параметра from и to обязательны'}, status=400)

    # Исправляем формат даты
    try:
        if 'T' in date_from:
            start_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        else:
            start_date = datetime.fromisoformat(date_from)
            end_date = datetime.fromisoformat(date_to)
    except ValueError:
        return Response({'error': 'Неверный формат даты'}, status=400)

    # Фильтрация данных с ограничением
    queryset = ElecReport.objects.filter(
        timestamp__date__gte=start_date.date(),
        timestamp__date__lte=end_date.date()
    )[:50000]  # Ограничиваем для предотвращения перегрузки
    
    if region:
        queryset = queryset.filter(region=region)
    
    if hour:
        queryset = queryset.filter(timestamp__hour=hour)

    # Подготовка данных для Excel
    data = []
    for record in queryset:
        row = {
            'Дата': record.timestamp.strftime('%Y-%m-%d'),
            'Время': record.timestamp.strftime('%H:%M'),
            'Регион': record.region,
            'Час': record.timestamp.hour
        }
        
        # Добавляем все числовые поля
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
    
    # Создание Excel файла
    if not data:
        return Response({'error': 'Нет данных для выбранного периода'}, status=404)
        
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
