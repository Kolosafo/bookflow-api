from rest_framework import serializers
from .models import BookInsight, Vendor, VendorAccount, BookROI


class BookInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookInsight
        fields = [
            'id',
            'book_title',
            'author_title',
            'insights',
            'actionable_steps',
            'generated_at'
        ]
        read_only_fields = ['id', 'generated_at']


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            'id',
            'name',
            'email',
            'plan',
            'daily_usage_limit',
            'daily_usage_count',
            'last_usage_reset',
            'is_active',
            'dropdown_preview_text',
            'created_at'
        ]
        read_only_fields = ['id', 'daily_usage_count', 'last_usage_reset', 'created_at']

    # Exclude sensitive api_key from serialization by default


class VendorDetailSerializer(serializers.ModelSerializer):
    """
    Detailed vendor serializer that includes API key for authenticated requests
    """
    class Meta:
        model = Vendor
        fields = [
            'id',
            'name',
            'email',
            'plan',
            'daily_usage_limit',
            'daily_usage_count',
            'last_usage_reset',
            'is_active',
            'dropdown_preview_text',
            'is_widget_open_by_default',
            'created_at'
        ]
        read_only_fields = ['id', 'daily_usage_count', 'last_usage_reset', 'created_at']


class VendorCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new vendor
    """
    class Meta:
        model = Vendor
        fields = [
            'id',
            'name',
            'email',
            'plan',
            'daily_usage_limit',
            'is_active',
        ]
        read_only_fields = ['id']

    def validate_email(self, value):
        """
        Check that the email is unique
        """
        if Vendor.objects.filter(email=value).exists():
            raise serializers.ValidationError("A vendor with this email already exists.")
        return value


# Vendor Authentication Serializers

class VendorSignUpSerializer(serializers.Serializer):
    """
    Serializer for vendor account sign up
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    website_url = serializers.URLField(required=False, allow_blank=True)
    company_name = serializers.CharField(max_length=255)

    def validate_email(self, value):
        """
        Check that the email is unique
        """
        if VendorAccount.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate(self, data):
        """
        Check that passwords match
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })
        return data

    def create(self, validated_data):
        """
        Create and return a new VendorAccount instance
        """
        validated_data.pop('confirm_password')
        vendor_account = VendorAccount.objects.create(**validated_data)
        return vendor_account


class VendorSignInSerializer(serializers.Serializer):
    """
    Serializer for vendor account sign in
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class VendorVerifyEmailSerializer(serializers.Serializer):
    """
    Serializer for vendor email verification
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4, min_length=4)


class VendorAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for vendor account details
    """
    vendor_id = serializers.CharField(source='vendor.id', read_only=True)
    vendor_plan = serializers.CharField(source='vendor.plan', read_only=True)
    user_id = serializers.CharField(source='user.id', read_only=True)
    user_type = serializers.CharField(source='user.type', read_only=True)

    class Meta:
        model = VendorAccount
        fields = [
            'id',
            'email',
            'company_name',
            'website_url',
            'status',
            'is_active',
            'created_at',
            'vendor_id',
            'vendor_plan',
            'user_id',
            'user_type'
        ]
        read_only_fields = ['id', 'status', 'created_at']


class BookROIRequestSerializer(serializers.Serializer):
    """
    Serializer for Book ROI request data
    """
    book_title = serializers.CharField(max_length=255)
    author = serializers.CharField(max_length=255, required=False, allow_blank=True)
    reader_goal = serializers.CharField()
    reader_challenge = serializers.CharField()
    available_time = serializers.CharField(max_length=100)


class BookROISerializer(serializers.ModelSerializer):
    """
    Serializer for Book ROI response data
    """
    class Meta:
        model = BookROI
        fields = [
            'id',
            'book_title',
            'author',
            'reader_goal',
            'reader_challenge',
            'available_time',
            'roi_score',
            'match_reasoning',
            'relevant_takeaways',
            'time_analysis',
            'estimated_reading_hours',
            'recommendation',
            'generated_at'
        ]
        read_only_fields = ['id', 'generated_at']
