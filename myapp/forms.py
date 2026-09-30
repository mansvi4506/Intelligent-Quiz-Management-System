from django import forms
from django.contrib.auth.models import User   # ✅ import User model
from .models import Profile   

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]  # ✅ editable fields

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "avatar", "preferences", "theme"]  # ✅ include avatar too too

# from .models import Quiz, Category, SubCategory

# class QuizForm(forms.ModelForm):
#     new_category = forms.CharField(required=False, help_text="Enter a new category if not listed")
#     new_subcategory = forms.CharField(required=False, help_text="Enter a new subcategory if not listed")

#     class Meta:
#         model = Quiz
#         fields = ['category', 'subcategory', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']

#     def save(self, commit=True):
#         quiz = super().save(commit=False)

#         # Handle new category
#         if self.cleaned_data['new_category']:
#             category, created = Category.objects.get_or_create(name=self.cleaned_data['new_category'])
#             quiz.category = category

#         # Handle new subcategory
#         if self.cleaned_data['new_subcategory']:
#             subcategory, created = SubCategory.objects.get_or_create(
#                 category=quiz.category,
#                 name=self.cleaned_data['new_subcategory']
#             )
#             quiz.subcategory = subcategory

#         if commit:
#             quiz.save()
#         return quiz
