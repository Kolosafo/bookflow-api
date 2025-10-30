
from rest_framework import serializers
from .models import NoteNotification

class NoteNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteNotification
        fields = '__all__'
      