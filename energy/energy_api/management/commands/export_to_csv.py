import os
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from energy_api.models import ElecReport

class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument('--from', type=str, required=True, help='Дата с (YYYY-MM-DD)')
        parser.add_argument('--to', type=str, required=True, help='Дата по (YYYY-MM-DD)')
        parser.add_argument('--region', type=str, help='Фильтр по региону')
        parser.add_argument('--hour', type=int, help='Фильтр по часу')
    
    def handle(self, *args, **options):
        date_from = options['from']
        date_to = options['to']
        region = options.get('region')
        hour = options.get('hour')
        

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"export_{date_from}_{date_to}_{timestamp}.csv"
        
        export_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
        os.makedirs(export_dir, exist_ok=True)
        file_path = os.path.join(export_dir, filename)
        

        file_url = f"{settings.MEDIA_URL}exports/{filename}"
        

        where_conditions = [
            f"timestamp >= '{date_from}'::date",
            f"timestamp <= '{date_to}'::date"
        ]
        
        if region:
            where_conditions.append(f"region = '{region}'")
        
        if hour is not None:
            where_conditions.append(f"hour = {hour}")
        
        where_clause = " AND ".join(where_conditions)
        

        sql = f"""
        COPY (
            SELECT 
                timestamp,
                region,
                hour,
                plan_ges, plan_aes, plan_tes, plan_ses, plan_ves, plan_other,
                techmin_ges, techmin_aes, techmin_tes, techmin_ses, techmin_ves, techmin_other,
                technomin_ges, technomin_aes, technomin_tes, technomin_ses, technomin_ves, technomin_other,
                techmax_ges, techmax_aes, techmax_tes, techmax_ses, techmax_ves, techmax_other,
                plan_consumption, plan_export, plan_import,
                price_buy, price_sell, full_plan
            FROM energy_api_elecreport
            WHERE {where_clause}
            ORDER BY timestamp, region, hour
        ) TO '{file_path}' 
        WITH (FORMAT CSV, HEADER true, DELIMITER ',', ENCODING 'UTF8');
        """
        
        with connection.cursor() as cursor:
            cursor.execute(sql)
        

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM energy_api_elecreport WHERE {where_clause}")
            count = cursor.fetchone()[0]
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Экспортировано {count} записей в {file_path}')
        )
        
        return {
            'file_path': file_path,
            'file_url': file_url,
            'count': count,
            'filename': filename
        }
