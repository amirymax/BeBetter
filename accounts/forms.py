from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    # Дополнительные поля
    birth_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Дата рождения"
    )
    category = forms.ChoiceField(
        choices=[('science', 'Наука'), ('art', 'Искусство'), ('health', 'Медицина'), ('sport', 'Спорт'), ('it', 'IT'), ('business', 'Бизнес')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Категория"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Пароль"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Подтверждение пароля"
    )

    class Meta:
        model = User
        fields = ['first_name', 'username', 'password']

    # Валидация паролей
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data


class UserEditForm(forms.ModelForm):
    # Поля, которые можно редактировать
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Имя"
    )
    username = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Имя пользователя"
    )
    birth_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Дата рождения"
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Новый пароль (необязательно)"
    )

    class Meta:
        model = User
        fields = ['first_name', 'username', 'password']

class UserProfileEditForm(forms.ModelForm):
    # Поле для отображения категории (read-only)
    category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Категория"
    )

    class Meta:
        model = UserProfile
        fields = [ 'category']
