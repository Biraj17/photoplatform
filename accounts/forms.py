import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils import timezone

from .models import Photographer, PhotographerProject, PortfolioImage


FIELD_CLASS = "field-input"

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .'\-]{2,}$")

_validate_email = EmailValidator(message="Enter a valid email address, like name@example.com.")
# A domain must have a name part and a real TLD, e.g. "gmail.com".
EMAIL_DOMAIN_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\.[a-z]{2,}$")


def clean_email_address(value):
    value = (value or "").strip().lower()
    if not value:
        raise ValidationError("Enter an email address.")
    _validate_email(value)
    # EmailValidator is lenient about the domain, so double-check it looks
    # like a real, routable domain with a proper TLD (e.g. "a@b" is rejected).
    domain = value.rsplit("@", 1)[-1]
    if ".." in value or not EMAIL_DOMAIN_RE.match(domain):
        raise ValidationError("Enter a valid email address, like name@example.com.")
    return value


def clean_nepali_mobile(value):
    digits = re.sub(r"\D", "", value or "")
    # Accept an optional +977 / 977 country code and normalise it away.
    if len(digits) == 13 and digits.startswith("977"):
        digits = digits[3:]
    if len(digits) != 10 or not digits.startswith("9"):
        raise ValidationError("Enter a valid 10-digit mobile number starting with 9 (e.g. 98XXXXXXXX).")
    return digits


def clean_person_name(value, field_label="name"):
    value = re.sub(r"\s+", " ", value.strip())
    if len(value) < 3:
        raise ValidationError(f"Enter your full {field_label} (at least 3 characters).")
    if not NAME_RE.match(value):
        raise ValidationError(f"The {field_label} can only contain letters, spaces, dots, hyphens and apostrophes.")
    return value


def clean_phone_number(value):
    value = value.strip()
    if not re.match(r"^\+?[\d\s\-]+$", value):
        raise ValidationError("Phone numbers can only contain digits, spaces, dashes and an optional leading +.")
    digits = re.sub(r"\D", "", value)
    if not 7 <= len(digits) <= 15:
        raise ValidationError("Enter a valid phone number (7 to 15 digits).")
    return value


class PhotographerJoinForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "field-input",
            "placeholder": "e.g. Sarita Gurung",
            "autocomplete": "name",
            "required": True,
        }),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "field-input",
            "placeholder": "you@example.com",
            "autocomplete": "email",
            "required": True,
        }),
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            "class": "field-input pr-11",
            "placeholder": "At least 8 characters",
            "autocomplete": "new-password",
            "required": True,
        }),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "field-input pr-11",
            "placeholder": "Re-enter your password",
            "autocomplete": "new-password",
            "required": True,
        }),
    )
    terms = forms.BooleanField(
        required=True,
        error_messages={"required": "You must agree to the Terms of Service and Privacy Policy."},
        widget=forms.CheckboxInput(attrs={"class": "mt-0.5 accent-[#C1684C]"}),
    )

    def clean_full_name(self):
        return clean_person_name(self.cleaned_data["full_name"])

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            raise forms.ValidationError("Password must contain at least one letter and one number.")
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data


class SignupOTPForm(forms.Form):
    code = forms.CharField(
        label="Verification code",
        min_length=6,
        max_length=6,
        widget=forms.TextInput(attrs={
            "class": "field-input text-center tracking-[0.5em] font-medium",
            "placeholder": "••••••",
            "inputmode": "numeric",
            "autocomplete": "one-time-code",
            "maxlength": "6",
            "required": True,
        }),
    )

    def clean_code(self):
        code = self.cleaned_data["code"].strip()
        if not code.isdigit():
            raise forms.ValidationError("The code contains 6 digits only.")
        return code


class PhotographerLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "class": FIELD_CLASS,
            "placeholder": "you@example.com",
            "autocomplete": "email",
            "required": True,
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": f"{FIELD_CLASS} pr-11",
            "placeholder": "Your password",
            "autocomplete": "current-password",
            "required": True,
        }),
    )


class PhotographerProfileForm(forms.ModelForm):
    OTHER_SPECIALTY = "Other"
    specialty = forms.ChoiceField(
        choices=Photographer.SPECIALTY_CHOICES + [(OTHER_SPECIALTY, "Other (type your own)")],
        widget=forms.Select(attrs={"class": FIELD_CLASS, "id": "id_specialty"}),
    )
    custom_specialty = forms.CharField(
        required=False,
        max_length=40,
        label="Your specialty / genre",
        widget=forms.TextInput(attrs={
            "class": FIELD_CLASS,
            "id": "id_custom_specialty",
            "placeholder": "e.g. Wildlife, Newborn, Product",
        }),
    )

    field_order = [
        "full_name",
        "city",
        "address",
        "phone",
        "contact_email",
        "specialty",
        "custom_specialty",
        "years_experience",
        "price_per_shoot",
        "bio",
        "profile_image",
    ]

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
            "full_name": forms.TextInput(attrs={"class": FIELD_CLASS, "required": True}),
            "city": forms.TextInput(attrs={"class": FIELD_CLASS}),
            "address": forms.TextInput(attrs={"class": FIELD_CLASS}),
            "phone": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "+977 98........"}),
            "contact_email": forms.EmailInput(attrs={"class": FIELD_CLASS}),
            "years_experience": forms.NumberInput(attrs={"class": FIELD_CLASS, "min": 0, "max": 60}),
            "price_per_shoot": forms.NumberInput(attrs={"class": FIELD_CLASS, "min": 0}),
            "bio": forms.Textarea(attrs={"class": FIELD_CLASS, "rows": 5}),
            "profile_image": forms.FileInput(attrs={"class": FIELD_CLASS, "accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        standard = [value for value, _ in Photographer.SPECIALTY_CHOICES]
        instance_specialty = getattr(self.instance, "specialty", "")
        if instance_specialty and instance_specialty not in standard:
            self.initial["specialty"] = self.OTHER_SPECIALTY
            self.initial["custom_specialty"] = instance_specialty

    def clean_full_name(self):
        return clean_person_name(self.cleaned_data["full_name"])

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if phone:
            return clean_phone_number(phone)
        return phone

    def clean_years_experience(self):
        years = self.cleaned_data["years_experience"]
        if years > 60:
            raise forms.ValidationError("Years of experience can't be more than 60.")
        return years

    def clean(self):
        cleaned_data = super().clean()
        specialty = cleaned_data.get("specialty")
        custom = (cleaned_data.get("custom_specialty") or "").strip()
        if specialty == self.OTHER_SPECIALTY:
            if len(custom) < 3:
                self.add_error("custom_specialty", "Type your specialty (at least 3 characters).")
            elif not re.match(r"^[A-Za-z][A-Za-z &/'\-]{2,39}$", custom):
                self.add_error("custom_specialty", "The specialty can only contain letters, spaces, &, / and hyphens.")
            else:
                cleaned_data["specialty"] = custom.title()
        return cleaned_data


class PhotographerKYCForm(forms.ModelForm):
    class Meta:
        model = Photographer
        fields = ["citizenship_number", "citizenship_front", "citizenship_back"]
        labels = {
            "citizenship_number": "Citizenship Number",
            "citizenship_front": "Citizenship Photo (Front)",
            "citizenship_back": "Citizenship Photo (Back)",
        }
        widgets = {
            "citizenship_number": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "e.g. 12-01-70-12345", "required": True}),
            "citizenship_front": forms.FileInput(attrs={"class": FIELD_CLASS, "accept": "image/*"}),
            "citizenship_back": forms.FileInput(attrs={"class": FIELD_CLASS, "accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Both document photos are compulsory; existing uploads satisfy the
        # requirement on re-submission.
        self.fields["citizenship_front"].required = True
        self.fields["citizenship_back"].required = True

    def clean_citizenship_number(self):
        number = self.cleaned_data["citizenship_number"].strip()
        if not re.match(r"^[\d][\d\-/ ]{3,39}$", number):
            raise forms.ValidationError("Enter a valid citizenship number (digits, dashes or slashes).")
        digits = re.sub(r"\D", "", number)
        if len(digits) < 4:
            raise forms.ValidationError("The citizenship number looks too short.")
        return number


class PortfolioImageForm(forms.ModelForm):
    class Meta:
        model = PortfolioImage
        fields = ["image", "caption"]
        widgets = {
            "image": forms.FileInput(attrs={"class": FIELD_CLASS, "accept": "image/*", "required": True}),
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
            "title": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "Project name", "required": True}),
            "location": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "Kathmandu, Nepal"}),
            "completed_at": forms.DateInput(attrs={"class": FIELD_CLASS, "type": "date"}),
            "description": forms.Textarea(attrs={"class": FIELD_CLASS, "rows": 4}),
            "cover_image": forms.FileInput(attrs={"class": FIELD_CLASS, "accept": "image/*"}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 3:
            raise forms.ValidationError("Give the project a name of at least 3 characters.")
        return title

    def clean_completed_at(self):
        completed_at = self.cleaned_data.get("completed_at")
        if completed_at and completed_at > timezone.localdate():
            raise forms.ValidationError("The completion date can't be in the future.")
        return completed_at
