from django.db import models
from account.utils import generate_id
from account.models import User

class ThemeCategory(models.TextChoices):
    MINDSET = "mindset", "Mindset"
    STRATEGY = "strategy", "Strategy"
    EXECUTION = "execution", "Execution"
    LEADERSHIP = "leadership", "Leadership"
    PERSONAL_DEVELOPMENT = "personal_development", "Personal Development"
    SYSTEMS = "systems", "Systems"
    RELATIONSHIPS = "relationships", "Relationships"
    OTHER = "other", "Other"


class MainArgument(models.Model):
    problem_identified = models.TextField()
    solution_proposed = models.TextField()
    why_it_matters = models.TextField()


class Framework(models.Model):
    name = models.CharField(max_length=255)
    overview = models.TextField()
    visual_representation = models.TextField(blank=True, null=True)


class FrameworkComponent(models.Model):
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, related_name="components")
    name = models.CharField(max_length=255)
    description = models.TextField()
    example = models.TextField()


class KeyInsight(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    theme = models.CharField(max_length=50, choices=ThemeCategory.choices)
    practical_application = models.TextField()
    supporting_quote = models.TextField(blank=True, null=True)


class ImplementationGuide(models.Model):
    overview = models.TextField()


class ImplementationStep(models.Model):
    guide = models.ForeignKey(ImplementationGuide, on_delete=models.CASCADE, related_name="steps")
    step_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    time_estimate = models.CharField(max_length=100, blank=True, null=True)
    resources_needed = models.JSONField(default=list)  # list of strings
    success_criteria = models.TextField()


class ImplementationMeta(models.Model):
    """Stores quick wins and pitfalls for each guide"""
    guide = models.OneToOneField(ImplementationGuide, on_delete=models.CASCADE, related_name="meta")
    common_pitfalls = models.JSONField(default=list)
    quick_wins = models.JSONField(default=list)


class OnePageSummary(models.Model):
    headline = models.CharField(max_length=255)
    core_message = models.TextField()
    key_principles = models.JSONField(default=list)
    actionable_takeaways = models.JSONField(default=list)
    memorable_quote = models.TextField()
    who_should_read = models.TextField()
    bottom_line = models.TextField()


class BookAnalysisResponse(models.Model):
    """Top-level model for saving the full analysis."""
    book_id = models.CharField(max_length=255, unique=True)
    book_title = models.CharField(max_length=255)
    book_author = models.CharField(max_length=255)
    main_argument = models.OneToOneField(MainArgument, on_delete=models.CASCADE, related_name="book_analysis")
    framework = models.OneToOneField(Framework, on_delete=models.SET_NULL, null=True, blank=True, related_name="book_analysis")
    implementation_guide = models.OneToOneField(ImplementationGuide, on_delete=models.CASCADE, related_name="book_analysis")
    one_page_summary = models.OneToOneField(OnePageSummary, on_delete=models.CASCADE, related_name="book_analysis")
    key_insights = models.ManyToManyField(KeyInsight, related_name="book_analyses")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.book_title}"



# OTHER MODELS
class UserExtractedBooks(models.Model):
    id = models.CharField(primary_key=True, default=generate_id(), editable=False, blank=True, max_length=100)
    book_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_extracted_book')
    book_title = models.CharField(max_length=255)
    book_img = models.CharField(max_length=500, blank=True, null=True)
    book_author = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.book_title}"
    

class BookmarkBook(models.Model):
    id = models.CharField(primary_key=True, default=generate_id(), editable=False, blank=True, max_length=100)
    book_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_marked_books')
    book_img = models.CharField(max_length=500, blank=True, null=True)
    book_title = models.CharField(max_length=255)
    book_author = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.book_title}"
    
    

class Notes(models.Model):
    id = models.CharField(primary_key=True, default=generate_id(), editable=False, blank=True, max_length=100)
    book_id = models.CharField(max_length=255)
    book_title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_note')
    content = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=255)
    book_author = models.CharField(max_length=255)
    note_type = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    def __str__(self):
        return f"{self.book_title}"