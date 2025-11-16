from django.db import models

class ElecReport(models.Model):
    region = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    hour = models.IntegerField()
    
    # План генерации
    plan_GES = models.FloatField(null=True, blank=True)
    plan_AES = models.FloatField(null=True, blank=True)
    plan_TES = models.FloatField(null=True, blank=True)
    plan_SES = models.FloatField(null=True, blank=True)
    plan_VES = models.FloatField(null=True, blank=True)
    plan_other = models.FloatField(null=True, blank=True)
    
    # Технологический минимум
    techmin_GES = models.FloatField(null=True, blank=True)
    techmin_AES = models.FloatField(null=True, blank=True)
    techmin_TES = models.FloatField(null=True, blank=True)
    techmin_SES = models.FloatField(null=True, blank=True)
    techmin_VES = models.FloatField(null=True, blank=True)
    techmin_other = models.FloatField(null=True, blank=True)
    
    # Технологический номинал
    technomin_GES = models.FloatField(null=True, blank=True)
    technomin_AES = models.FloatField(null=True, blank=True)
    technomin_TES = models.FloatField(null=True, blank=True)
    technomin_SES = models.FloatField(null=True, blank=True)
    technomin_VES = models.FloatField(null=True, blank=True)
    technomin_other = models.FloatField(null=True, blank=True)
    
    # Технологический максимум
    techmax_GES = models.FloatField(null=True, blank=True)
    techmax_AES = models.FloatField(null=True, blank=True)
    techmax_TES = models.FloatField(null=True, blank=True)
    techmax_SES = models.FloatField(null=True, blank=True)
    techmax_VES = models.FloatField(null=True, blank=True)
    techmax_other = models.FloatField(null=True, blank=True)
    
    # Потребление и экспорт/импорт
    plan_consumption = models.FloatField(null=True, blank=True)
    plan_export = models.FloatField(null=True, blank=True)
    plan_import = models.FloatField(null=True, blank=True)
    
    # Цены
    price_buy = models.FloatField(null=True, blank=True)
    price_sell = models.FloatField(null=True, blank=True)
    full_plan = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'elec_reports'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['region']),
        ]

    def __str__(self):
        return f"{self.region} - {self.timestamp}"

class LoadHistory(models.Model):
    data_date = models.DateField(primary_key=True)
    load_time = models.DateTimeField(auto_now=True)
    count = models.IntegerField(default=0)

    class Meta:
        db_table = 'load_history'

    def __str__(self):
        return f"Load {self.data_date} - {self.count} records"