# myapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib import messages
from .forms import ProfileUpdateForm, UserUpdateForm
from .models import Profile, Quiz, Category, SubCategory, QuizAttempt, AnswerAttempt
import json
import re
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .ai import get_ai_client


def _is_valid_topic_name(value):
    """Validate a human-readable quiz category or subcategory name."""
    value = " ".join(value.split())
    if not re.fullmatch(r"[A-Za-z][A-Za-z &'-]{1,48}[A-Za-z]", value):
        return False

    words = re.findall(r"[A-Za-z]+", value.lower())
    if not words or any(len(word) < 2 for word in words):
        return False

    # Reject common placeholder and keyboard/sequential input such as abc, abcd, qwerty.
    placeholders = {"abc", "abcd", "asdf", "qwerty", "test", "testing", "none", "null", "na", "n/a"}
    if value.lower() in placeholders:
        return False

    for word in words:
        if len(word) >= 3 and all(ord(word[index]) == ord(word[index - 1]) + 1 for index in range(1, len(word))):
            return False
        if len(set(word)) == 1:
            return False

    return True

# -------------------------------
# Dashboard → home page after login
# -------------------------------
@login_required(login_url='login')
def dashboard(request):
    quiz_history = QuizAttempt.objects.filter(user=request.user).order_by('-timestamp')[:5]
    return render(request, 'dashboard.html', {'quiz_history': quiz_history})

# -------------------------------
# Register → new user
# -------------------------------
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile
            Profile.objects.get_or_create(user=user)
            messages.success(request, "Account created successfully! Please login. 🎉")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# -------------------------------
# Profile → edit profile
# -------------------------------
@login_required(login_url='login')
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('dashboard')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {'u_form': u_form, 'p_form': p_form}
    return render(request, 'edit_profile.html', context)

# -------------------------------
# Quiz selection page
# -------------------------------
@login_required(login_url='login')
def quiz_view(request):
    categories = Category.objects.all()
    subcategories_dict = {cat.id: list(cat.subcategories.values('id', 'name')) for cat in categories}
    return render(request, 'quiz.html', {'categories': categories, 'subcategories_dict': subcategories_dict})

@login_required(login_url='login')
def select_subcategory(request, category_id):
    subcategories = SubCategory.objects.filter(category_id=category_id)
    return render(request, "select_subcategory.html", {"subcategories": subcategories})

@login_required(login_url='login')
def select_difficulty(request, subcategory_id):
    subcategory = SubCategory.objects.get(id=subcategory_id)
    difficulties = ["Easy", "Medium", "Hard"]
    return render(request, "select_difficulty.html", {"subcategory": subcategory, "difficulties": difficulties})

# -------------------------------
# Start quiz → generate questions
# -------------------------------
@login_required
def start_quiz(request, subcategory_id, difficulty, attempt_id=None):
    """
    Start a quiz based on category/subcategory and difficulty.
    Handles:
        - New typed category/subcategory (subcategory_id="new")
        - Existing dropdown selection
        - Retakes (attempt_id)
    """
    # ---------------------------
    # Case 1: User typed new category/subcategory
    # ---------------------------
    if subcategory_id == "new":
        new_cat_name = " ".join(request.GET.get("new_category", "").split())
        new_sub_name = " ".join(request.GET.get("new_subcategory", "").split())

        if not new_cat_name:
            messages.error(request, "A category is required.")
            return redirect('quiz')

        if not _is_valid_topic_name(new_cat_name):
            messages.error(request, "Enter a valid category name using real words (for example, 'World History').")
            return redirect('quiz')

        # A custom subcategory is optional; use a sensible default when it is omitted.
        new_sub_name = new_sub_name or "General"
        if not _is_valid_topic_name(new_sub_name):
            messages.error(request, "Enter a valid subcategory name using real words (for example, 'Ancient Civilizations').")
            return redirect('quiz')

        # Valid custom topics become available for future quizzes as well.
        category = Category.objects.filter(name__iexact=new_cat_name).first()
        if category is None:
            category = Category.objects.create(name=new_cat_name)

        subcategory = SubCategory.objects.filter(
            category=category, name__iexact=new_sub_name
        ).first()
        if subcategory is None:
            subcategory = SubCategory.objects.create(category=category, name=new_sub_name)

    # ---------------------------
    # Case 2: Existing dropdown selection
    # ---------------------------
    else:
        try:
            subcategory = SubCategory.objects.get(id=int(subcategory_id))
            category = subcategory.category
        except (SubCategory.DoesNotExist, ValueError):
            messages.error(request, "Selected subcategory does not exist.")
            return redirect('quiz')

    # ---------------------------
    # Case 3: Retake quiz
    # ---------------------------
    if attempt_id:
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
        questions = attempt.answers.all()
        return render(
            request,
            "start_quiz.html",
            {"questions": [ans.quiz for ans in questions], "attempt_id": attempt.id},
        )

    # ---------------------------
    # Generate new questions using OpenAI
    # ---------------------------
    old_questions = Quiz.objects.filter(
        subcategory=subcategory,
        difficulty=difficulty.lower()
    ).values_list("question", flat=True)

    prompt = f"""
    Generate 5 multiple-choice quiz questions.
    Category: {category.name}
    Subcategory: {subcategory.name}
    Difficulty: {difficulty}

    Do NOT repeat these questions: {list(old_questions)}

    Each question must have exactly 4 options and one correct answer.
    Respond in JSON array format like:
    [
      {{"question": "...", "option1": "...", "option2": "...", "option3": "...", "option4": "...", "correct_answer": "..."}},
      ...
    ]
    """

    try:
        response = get_ai_client().chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7,
        )
        content = response.choices[0].message.content
        questions = json.loads(content)
    except Exception:
        messages.error(request, "Error generating quiz questions. Try again.")
        return redirect('quiz')

    # Save quizzes in DB
    quiz_objects = []
    for q in questions:
        quiz = Quiz.objects.create(
            category=category,
            subcategory=subcategory,
            question=q["question"],
            difficulty=difficulty.lower(),
            option1=q["option1"],
            option2=q["option2"],
            option3=q["option3"],
            option4=q["option4"],
            correct_answer=q["correct_answer"],
        )
        quiz_objects.append(quiz)

    return render(request, "start_quiz.html", {"questions": quiz_objects})

# -------------------------------
# Submit quiz
# -------------------------------
@login_required
def submit_quiz(request):
    if request.method == "POST":
        score = 0
        total = 0
        for key, value in request.POST.items():
            if key.startswith("q"):
                quiz_id = key[1:]
                try:
                    quiz = Quiz.objects.get(id=quiz_id)
                except Quiz.DoesNotExist:
                    continue

                total += 1
                if value == quiz.correct_answer:
                    score += 1

        # Create attempt
        attempt = QuizAttempt.objects.create(
            user=request.user,
            category=quiz.category.name,
            subcategory=quiz.subcategory.name,
            difficulty=quiz.difficulty,
            score=score,
            total=total
        )

        request.session["last_attempt_id"] = attempt.id
        request.session["last_score"] = score
        request.session["last_total"] = total

        # Save answer attempts
        for key, value in request.POST.items():
            if key.startswith("q"):
                quiz_id = key[1:]
                try:
                    quiz = Quiz.objects.get(id=quiz_id)
                except Quiz.DoesNotExist:
                    continue
                AnswerAttempt.objects.create(
                    quiz_attempt=attempt,
                    quiz=quiz,
                    selected_answer=value,
                    is_correct=(value == quiz.correct_answer)
                )

        return redirect('quiz_results')

    return redirect('quiz')

# -------------------------------
# Quiz results
# -------------------------------
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import QuizAttempt

@login_required
def quiz_results(request):
    attempt_id = request.session.get("last_attempt_id")
    if not attempt_id:
        messages.error(request, "No quiz attempt found.")
        return redirect('quiz')

    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    answers = attempt.answers.all()

    # Generate explanations dynamically if missing and save to DB
    for ans in answers:
        if not ans.quiz.explanation:
            try:
                prompt = (
                    f"Question: {ans.quiz.question}\n"
                    f"Options:\nA) {ans.quiz.option1}\nB) {ans.quiz.option2}\n"
                    f"C) {ans.quiz.option3}\nD) {ans.quiz.option4}\n"
                    f"The correct answer is: {ans.quiz.correct_answer}\n\n"
                    "Explain in short why this answer is correct and why others are not."
                )
                response = get_ai_client().chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert quiz explainer."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=150,
                    temperature=0.7,
                )
                explanation_text = response.choices[0].message.content.strip()

                # Save explanation to DB
                ans.quiz.explanation = explanation_text
                ans.quiz.save(update_fields=['explanation'])

            except Exception as e:
                ans.quiz.explanation = "Explanation generation failed."
                ans.quiz.save(update_fields=['explanation'])

    return render(request, "quiz_results.html", {"attempt": attempt, "answers": answers})


# -------------------------------
# Retake Quiz
# -------------------------------
@login_required
def start_quiz_attempt(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    questions = attempt.answers.all()
    return render(request, "start_quiz.html", {"questions": [ans.quiz for ans in questions], "attempt_id": attempt.id})

# -------------------------------
# Quiz history
# -------------------------------
from django.db.models import Max

@login_required
def quiz_history(request):
    latest_per_quiz = (
        QuizAttempt.objects.filter(user=request.user)
        .values('category', 'subcategory', 'difficulty')
        .annotate(latest_timestamp=Max('timestamp'))
    )

    attempts = QuizAttempt.objects.filter(
        user=request.user,
        timestamp__in=[item['latest_timestamp'] for item in latest_per_quiz]
    ).order_by('-timestamp')

    return render(request, "quiz_history.html", {"attempts": attempts})

# -------------------------------
# Show answers
# -------------------------------
@login_required
def show_answers(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    answers = attempt.answers.all()
    return render(request, "show_answers.html", {"attempt": attempt, "answers": answers})

# -------------------------------
# Retake quiz → same questions
# -------------------------------
@login_required
def retake_quiz(request, attempt_id):
    old_attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    new_attempt = QuizAttempt.objects.create(
        user=request.user,
        category=old_attempt.category,
        subcategory=old_attempt.subcategory,
        difficulty=old_attempt.difficulty,
        score=0,
        total=old_attempt.total,
    )
    for ans in old_attempt.answers.all():
        AnswerAttempt.objects.create(
            quiz_attempt=new_attempt,
            quiz=ans.quiz,
            selected_answer='',
            is_correct=False
        )
    return redirect("start_quiz_attempt", attempt_id=new_attempt.id)

# -------------------------------
# LeaderBoard → Ranking Users 
# -------------------------------
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.shortcuts import render
from .models import QuizAttempt  # Your model for quiz attempts
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Avg
from .models import QuizAttempt, User

@login_required
def leaderboard(request):
    users_data = []
    all_users = User.objects.all()

    for user in all_users:
        attempts = QuizAttempt.objects.filter(user=user)
        total_attempts = attempts.count()
        avg_score = 0
        if total_attempts > 0:
            avg_score = sum([a.score for a in attempts]) / (total_attempts * 5) * 100  # Assuming each quiz max score = 5

        visit_count = getattr(user.profile, 'visit_count', 0) if hasattr(user, 'profile') else 0

        users_data.append({
            'username': user.username,
            'avg_score': avg_score,
            'attempts': total_attempts,
            'visit_count': visit_count
        })

    # Sort strictly by average score descending
    users_sorted = sorted(users_data, key=lambda x: x['avg_score'], reverse=True)

    # Top 3 users for medal display
    top_users = users_sorted[:3]

    context = {
        'users': users_sorted,
        'top_users': top_users
    }
    return render(request, 'leaderboard.html', context)

# In your app's views.py (e.g., quiz/views.py)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from django.db.models.functions import TruncDate

from .models import QuizAttempt, UserStreak, Badge, UserBadge

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import UserStreak

@login_required
def streaks_view(request):
    user = request.user
    today = timezone.now().date()

    # Get streak object, create if not exists
    streak_obj, created = UserStreak.objects.get_or_create(user=user)

    # Build streak history for the last 14 days (you can adjust this logic as needed)
    # Here, we assume days with streak continuity are 'active'
    streak_history = []
    last_date = streak_obj.last_completed_date or today

    # For simplicity, mark last streak days as active counting backwards from last_completed_date
    for i in range(14):
        check_date = today - timedelta(days=i)
        days_since_last = (last_date - check_date).days
        is_active = 0 <= days_since_last < streak_obj.current_streak
        streak_history.append({
            'date': check_date,
            'active': is_active
        })

    context = {
        'current_streak': streak_obj.current_streak,
        'longest_streak': streak_obj.longest_streak,
        'streak_history': streak_history,
    }
    return render(request, 'streaks.html', context)

@login_required
def badges_view(request):
    user = request.user
    total_quizzes = QuizAttempt.objects.filter(user=user).count()

    # Fetch user's existing badges
    user_badges = UserBadge.objects.filter(user=user).select_related('badge')
    earned_badge_names = set(ub.badge.name for ub in user_badges)

    # Fetch all possible badges
    possible_badges = Badge.objects.all()

    # Check criteria and assign new badges if needed
    for badge in possible_badges:
        if badge.name == "Beginner":
            if total_quizzes >= 1 and badge.name not in earned_badge_names:
                UserBadge.objects.create(user=user, badge=badge)
                messages.success(request, f'You earned the {badge.name} badge!')

        elif badge.name == "Quiz Enthusiast":
            if total_quizzes >= 10 and badge.name not in earned_badge_names:
                UserBadge.objects.create(user=user, badge=badge)
                messages.success(request, f'You earned the {badge.name} badge!')

        elif badge.name == "Quiz Master":
            high_score_quizzes = QuizAttempt.objects.filter(user=user, score__gte=90).count()
            if high_score_quizzes >= 50 and badge.name not in earned_badge_names:
                UserBadge.objects.create(user=user, badge=badge)
                messages.success(request, f'You earned the {badge.name} badge!')

        elif badge.name == "Streak Starter":
            try:
                streak = UserStreak.objects.get(user=user)
                if streak.current_streak >= 7 and badge.name not in earned_badge_names:
                    UserBadge.objects.create(user=user, badge=badge)
                    messages.success(request, f'You earned the {badge.name} badge!')
            except UserStreak.DoesNotExist:
                pass

    # Fetch updated badge list
    user_badges = UserBadge.objects.filter(user=user).select_related('badge')
    badge_list = [{
        'name': ub.badge.name,
        'icon': ub.badge.icon,
        'description': ub.badge.description,
    } for ub in user_badges]

    context = {
        'badges': badge_list,
        'total_badges': len(badge_list),
    }
    return render(request, 'badges.html', context)
