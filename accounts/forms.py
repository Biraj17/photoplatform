from django import forms
from django.contrib.auth.models import User

from .models import Photographer


class PhotographerJoinForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "field-input",
            "placeholder": "e.g. Sarita Gurung",
            "autocomplete": "name",
        }),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "field-input",
            "placeholder": "you@example.com",
            "autocomplete": "email",
        }),
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            "class": "field-input pr-11",
            "placeholder": "At least 8 characters",
            "autocomplete": "new-password",
        }),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "field-input pr-11",
            "placeholder": "Re-enter your password",
            "autocomplete": "new-password",
        }),
    )
    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "mt-0.5 accent-[#C1684C]"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self):
        email = self.cleaned_data["email"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data["password"],
        )
        photographer = Photographer.objects.create(
            user=user,
            full_name=self.cleaned_data["full_name"].strip(),
        )
        return photographer
