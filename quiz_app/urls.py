# Quiz application URL routes.
from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    # Authentication
    path('Quiz_Management_System/Login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('Quiz_Management_System/Register/', views.register, name='register'),
    path('Quiz_Management_System/Logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('Quiz_Management_System/About/', TemplateView.as_view(template_name="about.html"), name='about'),

    # Dashboard & profile
    path('Quiz_Management_System/Login/Dashboard/', views.dashboard, name='dashboard'),
    path('Quiz_Management_System/Login/Profile/', views.edit_profile, name='edit_profile'),

    path('Quiz_Management_System/Login/Dashboard/Quiz/Start/<str:subcategory_id>/<str:difficulty>/', views.start_quiz, name='start_quiz'),


    # Quiz selection & start
    path('Quiz_Management_System/Login/Dashboard/Quiz/', views.quiz_view, name='quiz'),
    path('Quiz_Management_System/Login/Dashboard/Quiz/Subcategory/<int:category_id>/', views.select_subcategory, name='select_subcategory'),
    path('Quiz_Management_System/Login/Dashboard/Quiz/Difficulty/<int:subcategory_id>/', views.select_difficulty, name='select_difficulty'),

    #Leaderboard 
    path('Quiz_Management_System/Login/Dashboard/leaderboard/', views.leaderboard, name='leaderboard'),

    # For retaking a quiz (creates new attempt)
    path('Quiz_Management_System/Login/Dashboard/Quiz/Retake/<int:attempt_id>/', views.retake_quiz, name='retake_quiz'),

    # Start quiz for an existing attempt (retake)
    path('Quiz_Management_System/Login/Dashboard/Quiz/Start-Attempt/<int:attempt_id>/', views.start_quiz_attempt, name='start_quiz_attempt'),

    # Quiz submission
    path('Quiz_Management_System/Login/Dashboard/Quiz/Submit/', views.submit_quiz, name='submit_quiz'),

    # Quiz results & history
    path('Quiz_Management_System/Login/Dashboard/Quiz/Results/', views.quiz_results, name='quiz_results'),
    path('Quiz_Management_System/Login/Dashboard/Quiz/History/', views.quiz_history, name='quiz_history'),

    # New URLs for Streaks and Badges (under Dashboard/, as siblings to leaderboard)
    path('Quiz_Management_System/Login/Dashboard/Streaks/', views.streaks_view, name='streaks'),
    path('Quiz_Management_System/Login/Dashboard/Badges/', views.badges_view, name='badges'),
    
    path('Quiz_Management_System/Login/Dashboard/Quiz/Show-Answers/<int:attempt_id>/', views.show_answers, name='show_answers'),
]



# urlpatterns = [
#     # Authentication
#     path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
#     path('register/', views.register, name='register'),
#     path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

#     path('about/', TemplateView.as_view(template_name="about.html"), name='about'),

#     # Dashboard & profile
#     path('dashboard/', views.dashboard, name='dashboard'),
#     path('profile/', views.edit_profile, name='edit_profile'),

#     # Quiz selection & start
#     path('quiz/', views.quiz_view, name='quiz'),
#     path("subcategory/<int:category_id>/", views.select_subcategory, name="select_subcategory"),
#     path("difficulty/<int:subcategory_id>/", views.select_difficulty, name="select_difficulty"),

#     # Start quiz (string allows "new" or ID)
#     # Quiz start
#     path('start_quiz/<str:subcategory_id>/<str:difficulty>/', views.start_quiz, name='start_quiz'),
#     # path("retake_quiz/<int:attempt_id>/", views.retake_quiz, name="retake_quiz"),
#     # path('start_quiz_attempt/<int:attempt_id>/', views.start_quiz, name='start_quiz_attempt'),
#     # For retaking a quiz (creates new attempt)
#     path("retake_quiz/<int:attempt_id>/", views.retake_quiz, name="retake_quiz"),

#     # Quiz submission
#     path('submit-quiz/', views.submit_quiz, name='submit_quiz'),

#     # Quiz results & history
#     path('quiz-results/', views.quiz_results, name='quiz_results'),
#     path('quiz-history/', views.quiz_history, name='quiz_history'),

#     path('show-answers/<int:attempt_id>/', views.show_answers, name='show_answers')

#     # Start quiz (string allows "new" or ID)
#     path('start_quiz/<str:subcategory_id>/<str:difficulty>/', views.start_quiz, name='start_quiz'),

#     # For retaking a quiz (creates new attempt)
#     path("retake_quiz/<int:attempt_id>/", views.retake_quiz, name="retake_quiz"),

#     # Start quiz for an existing attempt (retake)
#     path('start_quiz_attempt/<int:attempt_id>/', views.start_quiz, name='start_quiz_attempt'),

# ]
