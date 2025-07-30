from NEMO.models import BaseModel, User
from NEMO.views.constants import CHAR_FIELD_MEDIUM_LENGTH
from django.core.exceptions import ValidationError
from django.db import models


class Ethnicity(BaseModel):
    name = models.CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH, unique=True, help_text="The name of the ethnicity")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Ethnicities"
        ordering = ["name"]


class Race(BaseModel):
    name = models.CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH, unique=True, help_text="The name of the race")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Gender(BaseModel):
    name = models.CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH, unique=True, help_text="The name of the gender")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class EducationLevel(BaseModel):
    name = models.CharField(
        max_length=CHAR_FIELD_MEDIUM_LENGTH, unique=True, help_text="The name of the education level"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class UserDetails(BaseModel):
    user = models.OneToOneField(User, related_name="details", on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, null=True, blank=True, help_text="The user's gender", on_delete=models.SET_NULL)
    race = models.ForeignKey(Race, null=True, blank=True, help_text="The user's race", on_delete=models.SET_NULL)
    ethnicity = models.ForeignKey(
        Ethnicity, null=True, blank=True, help_text="The user's ethnicity", on_delete=models.SET_NULL
    )
    education_level = models.ForeignKey(
        EducationLevel, null=True, blank=True, help_text="The user's education level", on_delete=models.SET_NULL
    )
    emergency_contact = models.CharField(
        max_length=CHAR_FIELD_MEDIUM_LENGTH, blank=True, help_text="The user's emergency contact information"
    )
    phone_number = models.CharField(max_length=40, blank=True, help_text="The user's phone number")
    employee_id = models.CharField(
        max_length=CHAR_FIELD_MEDIUM_LENGTH, null=True, blank=True, help_text="The user's internal employee id"
    )
    orcid = models.CharField(
        verbose_name="ORCID", max_length=CHAR_FIELD_MEDIUM_LENGTH, null=True, blank=True, help_text="The user's ORCID"
    )
    scopus_id = models.CharField(
        verbose_name="Scopus ID",
        max_length=CHAR_FIELD_MEDIUM_LENGTH,
        null=True,
        blank=True,
        help_text="The user's Scopus ID",
    )
    researcher_id = models.CharField(
        verbose_name="Researcher ID",
        max_length=CHAR_FIELD_MEDIUM_LENGTH,
        null=True,
        blank=True,
        help_text="The user's Web of Science Researcher ID",
    )
    google_scholar_id = models.CharField(
        verbose_name="Google scholar ID",
        max_length=CHAR_FIELD_MEDIUM_LENGTH,
        null=True,
        blank=True,
        help_text="The user's Google Scholar ID",
    )

    def unique_identifier_field_names(self):
        return ["employee_id", "orcid", "scopus_id", "researcher_id", "google_scholar_id"]

    def clean(self):
        for field_name in self.unique_identifier_field_names():
            field_value = getattr(self, field_name)
            if field_value:
                not_unique = UserDetails.objects.filter(**{field_name: field_value}).exclude(id=self.id)
                if not_unique.exists():
                    raise ValidationError(
                        {field_name: f"A user with this {self._meta.get_field(field_name).name} already exists."}
                    )

    def __str__(self):
        return f"{self.user.get_name()}'s details"


def get_user_details(user: User):
    try:
        user_details = user.details
    except (UserDetails.DoesNotExist, AttributeError):
        user_details = UserDetails(user=user)
    return user_details
