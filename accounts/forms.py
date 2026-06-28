from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from .models import Photographer, PhotographerProject, PortfolioImage


FIELD_CLASS = "field-input"


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
            contact_email=email,
        )
        return photographer


class PhotographerLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "class": FIELD_CLASS,
            "placeholder": "you@example.com",
            "autocomplete": "email",
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": f"{FIELD_CLASS} pr-11",
            "placeholder": "Your password",
            "autocomplete": "current-password",
        }),
    )


class PhotographerProfileForm(forms.ModelForm):
    class Meta:
        model = Photographer
        fields = [
            "full_name",
            "city",
            "address",
            "phone",
            "contact_email",
            "specialty",
            "years_experience",
            "price_per_shoot",
            "bio",
            "profile_image",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": FIELD_CLASS}),
            "city": forms.TextInput(attrs={"class": FIELD_CLASS}),
            "address": forms.TextInput(attrs={"class": FIELD_CLASS}),
            "phone": forms.TextInput(attrs={"class": FIELD_CLASS}),
            "contact_email": forms.EmailInput(attrs={"class": FIELD_CLASS}),
            "specialty": forms.Select(attrs={"class": FIELD_CLASS}),
            "years_experience": forms.NumberInput(attrs={"class": FIELD_CLASS, "min": 0}),
            "price_per_shoot": forms.NumberInput(attrs={"class": FIELD_CLASS, "min": 0}),
            "bio": forms.Textarea(attrs={"class": FIELD_CLASS, "rows": 5}),
            "profile_image": forms.FileInput(attrs={"class": FIELD_CLASS, "accept": "image/*"}),
        }


class PortfolioImageForm(forms.ModelForm):
    class Meta:
        model = PortfolioImage
        fields = ["image", "caption"]
        widgets = {
            "image": forms.FileInput(attrs={"class": FIELD_CLASS, "accept": "image/*"}),
            "caption": forms.TextInput(attrs={
                "class": FIELD_CLASS,
                "placeholder": "Short caption",
            }),
        }


class PhotographerProjectForm(forms.ModelForm):
    class Meta:
        model = PhotographerProject
        fields = ["title", "location", "completed_at", "description", "cover_image"]
        widgets = {
            "title": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "Project name"}),
            "location": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "Kathmandu, Nepal"}),
            "completed_at": forms.DateInput(attrs={"class": FIELD_CLASS, "type": "date"}),
            "description": forms.Textarea(attrs={"class": FIELD_CLASS, "rows": 4}),
            "cover_image": forms.FileInput(attrs={"class": FIELD_CLASS, "accept": "image/*"}),
        }
