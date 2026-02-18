from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class SignupForm(forms.ModelForm):
    password1 = forms.CharField(label="Şifre", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Şifre (tekrar)", widget=forms.PasswordInput)

    # ✅ Rol alanını zorla göster
    role = forms.ChoiceField(
        label="Rol",
        choices=User.ROLE_CHOICES,
        widget=forms.Select,
        required=True,
    )

    class Meta:
        model = User
        fields = ["username", "email", "role"]

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Şifreler aynı değil.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)

        # ✅ ilk şifre her zaman 1234
        user.set_password("1234")

        # ✅ ilk girişte şifre değiştirsin
        user.must_change_password = True
        user.force_password_change = True

        # ✅ admin onayı gelene kadar beklesin
        user.is_approved = False
        user.is_active = True

        if commit:
            user.save()
        return user
