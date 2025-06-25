from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

User = get_user_model()


class RegisterForm(UserCreationForm):
    """
    Форма регистрации нового пользователя.
    Используется на странице регистрации.
    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class UserEditForm(UserChangeForm):
    """
    Форма редактирования профиля пользователя.
    Поле пароля скрыто — изменение пароля производится отдельно.
    """
    password = None

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class UserDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        label="Я подтверждаю удаление аккаунта",
        required=True
    )
