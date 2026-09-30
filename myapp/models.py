from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from .ai import get_ai_client


# ✅ Profile model (extends User)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    # age = models.PositiveIntegerField(null=True, blank=True)
    # gender = models.CharField(max_length=20, null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", default='avatars/default.png', blank=True, null=True) 
    preferences = models.CharField(max_length=255, blank=True, null=True)  # e.g. language, quiz type
    theme = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


# ✅ Category
# class Category(models.Model):
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name


# # ✅ SubCategory
# class SubCategory(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return f"{self.category.name} - {self.name}"

# Category model
# myapp/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('category', 'name')

    def __str__(self):
        return f"{self.category.name} - {self.name}"
    

# models.py
from django.db import models
from django.conf import settings
import openai

from django.db import models

class Quiz(models.Model):
    question = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    explanation = models.TextField(blank=True, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, default=1)
    difficulty = models.CharField(max_length=50, choices=[('Easy','Easy'),('Medium','Medium'),('Hard','Hard')])

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        # Only generate explanation if empty
        if not self.explanation:
            try:
                prompt = (
                    f"Question: {self.question}\n"
                    f"Options:\nA) {self.option1}\nB) {self.option2}\nC) {self.option3}\nD) {self.option4}\n"
                    f"Correct Answer: {self.correct_answer}\n\n"
                    "Give a **short explanation (1-2 sentences only)** why this answer is correct."
                )

                response = get_ai_client().chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert quiz explainer."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=60,  # short explanation
                    temperature=0.5,
                )

                explanation_text = response.choices[0].message.content.strip()
                self.explanation = explanation_text

            except Exception as e:
                self.explanation = f"Automatic explanation generation failed: {e}"

        super().save(*args, **kwargs)


# class Quiz(models.Model):
#     question = models.TextField()
#     option1 = models.CharField(max_length=200)
#     option2 = models.CharField(max_length=200)
#     option3 = models.CharField(max_length=200)
#     option4 = models.CharField(max_length=200)
#     correct_answer = models.CharField(max_length=200)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     explanation = models.TextField(blank=True, null=True)
#     subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, default=1)
#     difficulty = models.CharField(max_length=50, choices=[('Easy','Easy'),('Medium','Medium'),('Hard','Hard')])

#     def __str__(self):
#         return self.question


# ✅ Difficulty Level
DIFFICULTY_CHOICES = [
    ("easy", "Easy"),
    ("medium", "Medium"),
    ("hard", "Hard"),
]

# ✅ Quiz
# class Quiz(models.Model):
#     difficulty = models.CharField(max_length=50, default="Easy")
#     question = models.TextField()
#     option1 = models.CharField(max_length=255, default="")
#     option2 = models.CharField(max_length=255, default="")
#     option3 = models.CharField(max_length=255, default="")
#     option4 = models.CharField(max_length=255, default="")
#     correct_answer = models.CharField(max_length=255, default="")

#     def __str__(self):
#         return self.question[:50]

# Quiz model (restore foreign key relationships)
# class Quiz(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)  # no extra quote
#     difficulty = models.CharField(max_length=50, default="Easy")
#     question = models.TextField()
#     option1 = models.CharField(max_length=255, default="")
#     option2 = models.CharField(max_length=255, default="")
#     option3 = models.CharField(max_length=255, default="")
#     option4 = models.CharField(max_length=255, default="")
#     correct_answer = models.CharField(max_length=255, default="")

#     def __str__(self):
#         return self.question[:50]

from django.db import models
from django.contrib.auth.models import User

class QuizHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    date_taken = models.DateTimeField(auto_now_add=True)
    explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score})"



# ✅ QuizAttempt
class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, default="Unknown")   
    subcategory = models.CharField(max_length=100, default="General")   # ✅ already stored     
    # subcategory = models.CharField(max_length=100, default="Unknown")     
    difficulty = models.CharField(max_length=50, default="Easy")         
    score = models.IntegerField(default=0)                                
    total = models.IntegerField(default=1)                                 
    timestamp = models.DateTimeField(auto_now_add=True)
    # avg_score_percent = (sum([a.score for a in attempts]) / (total_attempts * 100)) * 100
    
    def __str__(self):
        return f"{self.user} - {self.category} ({self.score}/{self.total})"

# ✅ Answers
class AnswerAttempt(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="answers")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"{self.quiz_attempt.user} - {self.quiz.question[:30]} - {self.is_correct}"

# Simple Streak model (optional; can calculate on-the-fly from QuizAttempt)
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta

class UserStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_completed_date = models.DateField(null=True, blank=True)

    def update_streak(self):
        today = timezone.now().date()
        if self.last_completed_date == today - timedelta(days=1):
            self.current_streak += 1
        elif self.last_completed_date != today:
            self.current_streak = 1
        # else: last_completed_date == today, do nothing (already updated)
        self.longest_streak = max(self.longest_streak, self.current_streak)
        self.last_completed_date = today
        self.save()

    def __str__(self):
        return f"{self.user.username} - Current: {self.current_streak}, Longest: {self.longest_streak}"

        

class Badge(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default='🏅')  # Emoji or icon code
    description = models.TextField()
    criteria = models.CharField(max_length=200)  # e.g., "Complete 10 quizzes"
    
    def __str__(self):
        return self.name
    
# Badge model
from django.contrib.auth.models import User

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')  # Prevent duplicates

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
