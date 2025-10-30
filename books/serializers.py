from rest_framework import serializers
from .models import (
    BookmarkBook,
    UserExtractedBooks,
    MainArgument,
    Framework,
    FrameworkComponent,
    KeyInsight,
    ImplementationGuide,
    ImplementationStep,
    ImplementationMeta,
    OnePageSummary,
    BookAnalysisResponse,
    Notes
)


# ------------------ BASIC SERIALIZERS ------------------

class MainArgumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainArgument
        fields = "__all__"


class FrameworkComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrameworkComponent
        fields = "__all__"


class FrameworkSerializer(serializers.ModelSerializer):
    components = FrameworkComponentSerializer(many=True, read_only=True)

    class Meta:
        model = Framework
        fields = ["id", "name", "overview", "visual_representation", "components"]


class KeyInsightSerializer(serializers.ModelSerializer):
    theme_display = serializers.CharField(source="get_theme_display", read_only=True)

    class Meta:
        model = KeyInsight
        fields = [
            "id",
            "title",
            "description",
            "theme",
            "theme_display",
            "practical_application",
            "supporting_quote",
        ]


class ImplementationStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImplementationStep
        fields = "__all__"


class ImplementationMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImplementationMeta
        fields = ["common_pitfalls", "quick_wins"]


class ImplementationGuideSerializer(serializers.ModelSerializer):
    steps = ImplementationStepSerializer(many=True, read_only=True)
    meta = ImplementationMetaSerializer(read_only=True)

    class Meta:
        model = ImplementationGuide
        fields = ["id", "overview", "steps", "meta"]


class OnePageSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = OnePageSummary
        fields = "__all__"


# ------------------ MAIN NESTED SERIALIZER ------------------

class BookAnalysisResponseSerializer(serializers.ModelSerializer):
    main_argument = MainArgumentSerializer()
    framework = FrameworkSerializer(allow_null=True)
    implementation_guide = ImplementationGuideSerializer()
    one_page_summary = OnePageSummarySerializer()
    key_insights = KeyInsightSerializer(many=True)

    class Meta:
        model = BookAnalysisResponse
        fields = [
            "id",
            "book_title",
            "book_author",
            "main_argument",
            "framework",
            "implementation_guide",
            "one_page_summary",
            "key_insights",
            "created_at",
            "updated_at",
        ]




class UserExtractedBooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserExtractedBooks
        fields = "__all__"
        

class BookmarkBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookmarkBook
        fields = "__all__"
        

class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = [
            'id',
            'user',
            'book_id',
            'book_title',
            'content',
            'title',
            'book_author',
            'has_notification',
            'note_type',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']