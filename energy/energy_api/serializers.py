# energy_api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ElecReport, LoadHistory, UserProfile


class ElecReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecReport
        fields = '__all__'


class LoadHistorySerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    loaded = serializers.SerializerMethodField()

    class Meta:
        model = LoadHistory
        fields = ['date', 'loaded', 'count']

    def get_date(self, obj):
        return obj.data_date.strftime('%d.%m.%Y')

    def get_loaded(self, obj):
        return obj.load_time.strftime('%Y-%m-%d %H:%M:%S')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['region', 'role', 'organization', 'course', 'specialization']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
