# yourapp/serializers.py
from rest_framework import serializers
from .models import User, PrivacyPolicy, TermsOfUse, SupportMessage, UserSubscriptionUsage

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', "deviceId", 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        return user



class BioAuthSerializer(serializers.ModelSerializer):
    subscription = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
                    'email',
                    'deviceId',
                    'id',
                    'status',
                    'interests',
                    'subscription',
                    'free_trail',
                    'date_subscription_ends',
                    'date_subscribed'
                  ]

    def get_subscription(self, obj):
        # If user has a free trial, pretend it's a monthly premium
        return "monthly premium" if obj.free_trail else obj.subscription
    
    
    
        

class PrivacyPolicySerializer(serializers.ModelSerializer):
    content_html = serializers.SerializerMethodField()
    
    class Meta:
        model = PrivacyPolicy
        fields = ['id', 'title', 'content', 'content_html', 'created_at', 'updated_at']
    
    def get_content_html(self, obj):
        return obj.get_content_html()
    

class UserInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['interests']
        
    
class TermsOfUsSerializer(serializers.ModelSerializer):
    content_html = serializers.SerializerMethodField()
    
    class Meta:
        model = TermsOfUse
        fields = ['id', 'title', 'content', 'content_html', 'created_at', 'updated_at']
    
    def get_content_html(self, obj):
        return obj.get_content_html()
    



class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ['id', 'email', 'message', 'isResolved']
      
      

class SubscriptionUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscriptionUsage
        fields = '__all__'
   