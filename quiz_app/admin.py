from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Profile, Quiz, QuizAttempt

# Remove Groups from admin (optional)
admin.site.unregister(Group)

# ----------------------------
# Profile Admin
# ----------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "theme", "preferences", "total_score")

    def total_score(self, obj):
        # Sum all quiz attempt scores for this user
        return sum(attempt.score for attempt in QuizAttempt.objects.filter(user=obj.user))
    total_score.short_description = "Total Score"

# ----------------------------
# Quiz Admin
# ----------------------------
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("question", "category" ,"difficulty", "correct_answer")

# ----------------------------
# QuizAttempt Admin
# ----------------------------
# First, make sure it is not already registered
try:
    admin.site.unregister(QuizAttempt)
except admin.sites.NotRegistered:
    pass

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "subcategory", "difficulty", "score", "total", "timestamp")
    list_filter = ("category", "subcategory", "difficulty", "timestamp")
    search_fields = ("user__username", "category__name", "subcategory__name")

from django.contrib import admin
from .models import Badge, UserBadge

admin.site.register(Badge)
admin.site.register(UserBadge)
