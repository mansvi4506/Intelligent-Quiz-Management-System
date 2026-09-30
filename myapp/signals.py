from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from django.db.models.signals import post_migrate
from .models import Category, SubCategory

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    if sender.name == 'myapp':
        data = {
            "Academic": ["Math", "Science", "History", "Geography", "Computer Science", "Languages"],
            "Technology & IT": ["Programming", "Web Development", "Cybersecurity", "Data Science", "Networking"],
            "General Knowledge": ["Current Affairs", "Politics & Government", "Economics", "World Events", "Books & Authors"],
            "Entertainment": ["Movies", "TV Shows", "Music", "Celebrities", "Gaming"],
            "Sports": ["Football", "Cricket", "Olympics", "Tennis", "Esports"],
            "Logical & Aptitude": ["Reasoning", "Puzzles", "Quantitative Aptitude", "Verbal Ability"],
            "Fun & Miscellaneous": ["Memes & Pop Culture", "Travel & Places", "Food & Cuisine", "Art & Photography"]
        }

        for cat_name, subcats in data.items():
            cat, created = Category.objects.get_or_create(name=cat_name)
            for sub in subcats:
                SubCategory.objects.get_or_create(category=cat, name=sub)



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Only save if profile already exists
    if hasattr(instance, "profile"):
        instance.profile.save()

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import UserStreak  # Adjust import based on your app structure

import logging
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from datetime import timedelta
from .models import UserStreak

# logger = logging.getLogger(__name__)

# @receiver(user_logged_in)
# def update_streak_on_login(sender, request, user, **kwargs):
#     logger.info(f"User {user.username} logged in - updating streak")
#     streak, created = UserStreak.objects.get_or_create(user=user)
#     today = timezone.now().date()

#     logger.info(f"Before update: current_streak={streak.current_streak}, last_completed_date={streak.last_completed_date}")

#     if streak.last_completed_date == today:
#         # Already updated today, do nothing
#         pass
#     elif streak.last_completed_date == today - timedelta(days=1):
#         streak.current_streak += 1
#     else:
#         streak.current_streak = 1

#     streak.longest_streak = max(streak.longest_streak, streak.current_streak)
#     streak.last_completed_date = today
#     streak.save()

#     logger.info(f"After update: current_streak={streak.current_streak}, last_completed_date={streak.last_completed_date}")
@receiver(user_logged_in)
def update_streak_on_login(sender, request, user, **kwargs):
    streak, created = UserStreak.objects.get_or_create(user=user)
    today = timezone.now().date()

    print(f"Before update: current_streak={streak.current_streak}, last_completed_date={streak.last_completed_date}")

    if streak.last_completed_date is None:
        print("Last completed date is None, setting current_streak to 1")
        streak.current_streak = 1
    elif streak.last_completed_date == today - timedelta(days=1):
        print("Last completed date was yesterday, incrementing streak")
        streak.current_streak += 1
    elif streak.last_completed_date == today:
        if streak.current_streak == 0:
            print("Last completed date is today but current_streak is zero; initializing to 1")
            streak.current_streak = 1
        else:
            print("Already logged in today, no change")
        # do nothing else
    else:
        print("Last completed date is older than yesterday, resetting streak to 1")
        streak.current_streak = 1

    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    streak.last_completed_date = today
    streak.save()

    print(f"After update: current_streak={streak.current_streak}, longest_streak={streak.longest_streak}, last_completed_date={streak.last_completed_date}")
