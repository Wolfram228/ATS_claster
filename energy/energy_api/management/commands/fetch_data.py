import warnings
from urllib3.exceptions import InsecureRequestWarning
import requests
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta, time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from zoneinfo import ZoneInfo

from energy_api.models import ElecReport, LoadHistory

warnings.simplefilter('ignore', InsecureRequestWarning)

class Command(BaseCommand):
    help = 'Загрузка данных энергетики с ATSenergo'
    
    COLS = [
        'region','hour',
        'plan_GES','plan_AES','plan_TES','plan_SES','plan_VES','plan_other',
        'techmin_GES','techmin_AES','techmin_TES','techmin_SES','techmin_VES','techmin_other',
        'technomin_GES','technomin_AES','technomin_TES','technomin_SES','technomin_VES','technomin_other',
        'techmax_GES','techmax_AES','techmax_TES','techmax_SES','techmax_VES','techmax_other',
        'plan_consumption','plan_export','plan_import',
        'price_buy','price_sell','full_plan'
    ]
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/vnd.ms-excel,*/*;q=0.9',
        'Referer': 'https://www.atsenergo.ru/'
    }

    def download_xls(self, date):
        """Скачать XLS за конкретную дату"""
        ds = date.strftime('%Y%m%d')
        url_page = f'https://www.atsenergo.ru/nreport?rname=trade_region_spub&rdate={ds}'
        
        page = requests.get(url_page, headers=self.HEADERS, verify=False)
        page.raise_for_status()

        soup = BeautifulSoup(page.content, 'html.parser')
        link = soup.find('a', href=lambda h: h and 'fid=' in h)
        if not link:
            raise ValueError("Нет .xls ссылки на странице")
        
        file_url = urljoin(page.url, link['href'])
        resp = requests.get(file_url, headers=self.HEADERS, verify=False)
        resp.raise_for_status()
        
        return BytesIO(resp.content)

    def handle(self, *args, **options):
        """Основная логика команды"""
        self.stdout.write('Начало загрузки данных...')
        
        # Загрузка за последние 2 года
        today = datetime.today().date()
        start_date = today - timedelta(days=730)  # 2 года = 730 дней
        
        current_date = datetime.combine(start_date, time(0))
        end_date = datetime.combine(today, time(0))
        loaded_count = 0
        
        self.stdout.write(f'Загрузка данных с {start_date} по {today}')
        
        while current_date <= end_date:
            try:
                # Пропускаем будущие даты
                if current_date.date() > today:
                    current_date += timedelta(days=1)
                    continue
                    
                # Проверяем, есть ли уже данные за эту дату
                exists = LoadHistory.objects.filter(data_date=current_date.date()).first()
                if not exists or exists.count == 0:
                    bio = self.download_xls(current_date)
                    df = pd.read_excel(bio, skiprows=5, header=0, names=self.COLS, engine='xlrd')
                    
                    inserted = self.save_data(df, current_date)
                    loaded_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"{current_date.date()}: ЗАГРУЖЕНО {inserted} записей")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"{current_date.date()}: ОШИБКА - {e}")
                )
            
            current_date += timedelta(days=1)
        
        self.stdout.write(
            self.style.SUCCESS(f'Загрузка завершена. Обработано дней: {loaded_count}')
        )
    
    @transaction.atomic
    def save_data(self, df, date):
        """Сохранение данных в базу"""
        inserted = 0
        irkutsk_tz = ZoneInfo("Asia/Irkutsk")
        
        for _, row in df.iterrows():
            # Пропускаем строки с NaN в hour
            if pd.isnull(row['hour']):
                continue
                
            hour_val = int(row['hour'])
            
            # Пропускаем некорректные часы
            if hour_val < 0 or hour_val > 23:
                continue

            naive_dt = datetime.combine(date.date(), time(hour_val, 0))
            aware_dt = naive_dt.replace(tzinfo=irkutsk_tz)

            data_dict = {}
            for col in self.COLS[2:]:
                value = row[col]
                data_dict[col] = float(value) if pd.notnull(value) else None

            ElecReport.objects.create(
                region=row['region'],
                hour=hour_val,
                timestamp=aware_dt,
                **data_dict
            )
            inserted += 1
        
        LoadHistory.objects.update_or_create(
            data_date=date.date(),
            defaults={
                'load_time': timezone.now(),
                'count': inserted
            }
        )
        return inserted
