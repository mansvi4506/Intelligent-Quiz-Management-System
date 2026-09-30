from django.apps import AppConfig

class QuizAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quiz_app'
    # Keep the existing Django app label so migrations and database tables remain compatible.
    label = 'myapp'

    def ready(self):
        import quiz_app.signals


