from django.db import models
from django.contrib.auth.models import User

class ElecReport(models.Model):
    region = models.CharField(max_length=255)
    timestamp = models.DateField()
    hour = models.IntegerField()
    plan_GES = models.FloatField(null=True, blank=True)
    plan_AES = models.FloatField(null=True, blank=True)
    plan_TES = models.FloatField(null=True, blank=True)
    plan_SES = models.FloatField(null=True, blank=True)
    plan_VES = models.FloatField(null=True, blank=True)
    plan_other = models.FloatField(null=True, blank=True)
    techmin_GES = models.FloatField(null=True, blank=True)
    techmin_AES = models.FloatField(null=True, blank=True)
    techmin_TES = models.FloatField(null=True, blank=True)
    techmin_SES = models.FloatField(null=True, blank=True)
    techmin_VES = models.FloatField(null=True, blank=True)
    techmin_other = models.FloatField(null=True, blank=True)
    technomin_GES = models.FloatField(null=True, blank=True)
    technomin_AES = models.FloatField(null=True, blank=True)
    technomin_TES = models.FloatField(null=True, blank=True)
    technomin_SES = models.FloatField(null=True, blank=True)
    technomin_VES = models.FloatField(null=True, blank=True)
    technomin_other = models.FloatField(null=True, blank=True)
    techmax_GES = models.FloatField(null=True, blank=True)
    techmax_AES = models.FloatField(null=True, blank=True)
    techmax_TES = models.FloatField(null=True, blank=True)
    techmax_SES = models.FloatField(null=True, blank=True)
    techmax_VES = models.FloatField(null=True, blank=True)
    techmax_other = models.FloatField(null=True, blank=True)
    plan_consumption = models.FloatField(null=True, blank=True)
    plan_export = models.FloatField(null=True, blank=True)
    plan_import = models.FloatField(null=True, blank=True)
    price_buy = models.FloatField(null=True, blank=True)
    price_sell = models.FloatField(null=True, blank=True)
    full_plan = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'elec_reports'

    def __str__(self):
        return f"{self.region} - {self.timestamp} - {self.hour}"


class LoadHistory(models.Model):
    data_date = models.DateField(primary_key=True)
    load_time = models.DateTimeField()
    count = models.IntegerField()

    class Meta:
        db_table = 'load_history'

    def __str__(self):
        return f"{self.data_date} - {self.count} записей"

class LoadHistory(models.Model):
    data_date = models.DateField(primary_key=True)
    load_time = models.DateTimeField()
    count = models.IntegerField()

    class Meta:
        db_table = 'load_history'

    def __str__(self):
        return f"{self.data_date} - {self.count} записей"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('admin', 'Администратор'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    region = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='student')
    organization = models.CharField(max_length=255, blank=True, null=True)
    course = models.IntegerField(blank=True, null=True)
    specialization = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
