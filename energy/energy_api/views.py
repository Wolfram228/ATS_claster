import json
from datetime import datetime, timedelta, date
from django.shortcuts import render
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.db.models import Sum, Avg
from django.utils import timezone
from .models import ElecReport

@cache_page(60 * 5)  # Кэшируем на 5 минут
def index(request):
    """Главная страница с графиками и статистикой"""
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