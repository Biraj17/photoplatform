from django import forms
from django.utils import timezone

from accounts.forms import clean_email_address, clean_nepali_mobile, clean_person_name
from accounts.models import Photographer

from .models import BookingRequest, Offer


FIELD_CLASS = "field-input"


class PhotographerSearchForm(forms.Form):
    specialty = forms.ChoiceField(
        required=False,
        choices=[("", "All categories")] + Photographer.SPECIALTY_CHOICES,
        widget=forms.Select(attrs={"class": "w-full bg-transparent font-display text-lg italic focus:outline-none"}),
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full bg-transparent font-display text-lg italic placeholder:text-bark/50 focus:outline-none",
            "placeholder": "Kathmandu, Pokhara",
        }),
    )
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "w-full bg-transparent font-display text-lg italic placeholder:text-bark/50 focus:outline-none",
            "type": "date",
        }),
    )


class BookingRequestForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ["client_phone", "client_name", "client_email", "shoot_date", "package", "message"]
        labels = {
            "client_phone": "Phone Number",
            "client_name": "Full Name",
            "client_email": "Email Address",
            "shoot_date": "Preferred Date",
        }
        widgets = {
            "client_phone": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "98XXXXXXXX", "inputmode": "numeric", "maxlength": "14", "required": True}),
            "client_name": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "Your name", "required": True}),
            "client_email": forms.EmailInput(attrs={"class": FIELD_CLASS, "placeholder": "you@example.com", "required": True}),
            "shoot_date": forms.DateInput(attrs={"class": FIELD_CLASS, "type": "date", "required": True}),
            "package": forms.Select(attrs={"class": FIELD_CLASS}),
            "message": forms.Textarea(attrs={"class": FIELD_CLASS, "rows": 4, "placeholder": "Tell the photographer about the shoot", "required": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The date picker shouldn't offer days in the past.
        self.fields["shoot_date"].widget.attrs["min"] = timezone.localdate().isoformat()

    def clean_client_name(self):
        return clean_person_name(self.cleaned_data["client_name"])

    def clean_client_phone(self):
        return clean_nepali_mobile(self.cleaned_data["client_phone"])

    def clean_client_email(self):
        return clean_email_address(self.cleaned_data["client_email"])

    def clean_shoot_date(self):
        shoot_date = self.cleaned_data["shoot_date"]
        if shoot_date < timezone.localdate():
            raise forms.ValidationError("The shoot date can't be in the past.")
        return shoot_date

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 10:
            raise forms.ValidationError("Tell the photographer a little more about the shoot (at least 10 characters).")
        return message


class PhotographerOfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["title", "discount_percent", "description", "ends_at"]
        labels = {
            "title": "Offer Title",
            "discount_percent": "Discount %",
            "ends_at": "Valid Until",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "e.g. Off-season wedding discount", "required": True}),
            "discount_percent": forms.NumberInput(attrs={"class": FIELD_CLASS, "min": 1, "max": 100, "required": True}),
            "description": forms.Textarea(attrs={"class": FIELD_CLASS, "rows": 3, "placeholder": "What's included in this offer", "required": True}),
            "ends_at": forms.DateInput(attrs={"class": FIELD_CLASS, "type": "date", "required": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ends_at"].widget.attrs["min"] = timezone.localdate().isoformat()

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 3:
            raise forms.ValidationError("Give the offer a title of at least 3 characters.")
        return title

    def clean_discount_percent(self):
        discount = self.cleaned_data["discount_percent"]
        if not 1 <= discount <= 100:
            raise forms.ValidationError("The discount must be between 1% and 100%.")
        return discount

    def clean_ends_at(self):
        ends_at = self.cleaned_data["ends_at"]
        if ends_at < timezone.localdate():
            raise forms.ValidationError("The end date can't be in the past.")
        return ends_at
