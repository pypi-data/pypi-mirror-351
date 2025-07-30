from uuid import uuid4

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    first_name = models.CharField(max_length=255, default="John")
    last_name = models.CharField(max_length=255, default="Doe")
    gender = models.CharField(
        max_length=255,
        verbose_name=_("Gender"),
        default="active",
        choices=(("female", "female"), ("1", "male")),
    )
    date_of_birth = models.DateField(blank=True, null=True)
    slug = models.SlugField(default=uuid4, verbose_name="Author id")

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    def get_name_label(self):
        return "Foobar"

    def get_slug_display(self):
        return f"Fancy slug {self.slug}"
    get_slug_display.short_description = _("Fancy slug label")

    @property
    def label(self):
        return "Author"

    @property
    def first_name_localized(self):
        return _(self.first_name)
    first_name_localized.fget.short_description = _("Translated first name")

    class Meta:
        verbose_name = "Book author"
        verbose_name_plural = "Book authors"


class Award(models.Model):
    name = models.CharField(max_length=255)
    author = models.ForeignKey(Author, related_name="awards", on_delete=models.CASCADE)
    slug = models.SlugField(default=uuid4, verbose_name="Award id")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Award"
        verbose_name_plural = "Awards"


class Conference(models.Model):
    name = models.CharField(max_length=255)
    event_date = models.DateField()

    @property
    def full_name(self):
        return f"{self.name} - {self.event_date}"

    @property
    def full_name_localized(self):
        return f"{self.name} - {self.event_date} foo"
    full_name_localized.fget.short_description = _("Localized full name")

    def get_days_until(self):
        today = timezone.now().date()
        return self.event_date - today

    def get_days_after(self):
        today = timezone.now().date()
        return today - self.event_date
    get_days_after.short_description = _("Days after conference")


class Company(models.Model):
    name = models.CharField(max_length=255, default="Foo Bar Inc")

    def get_absolute_url(self):
        return "https://example.com"

    class Meta:
        verbose_name = "Firm"


class Publisher(models.Model):
    name = models.CharField(max_length=255, default="Foo Bar")
    conferences = models.ManyToManyField(Conference)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("publisher-detail", kwargs={"pk": self.pk})


class Book(models.Model):
    authors = models.ManyToManyField(Author, verbose_name="writers")
    awards = models.ManyToManyField(Award)
    publisher = models.ForeignKey(
        Publisher, on_delete=models.PROTECT, verbose_name="publishing house"
    )
    avg_rating = models.DecimalField(default=4.55, decimal_places=2, max_digits=3)
    available = models.BooleanField(default=True)
    date_published = models.DateField(default=timezone.now)
    last_updated = models.DateTimeField(default=timezone.now)
    stock = models.IntegerField(default=10)
    title = models.CharField(max_length=255, default="Lorem Ipsum")
    random_set = models.CharField(
        max_length=255, default="Lorem Lorem", verbose_name="random set"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Boek"
        verbose_name_plural = "Boeken"
        ordering = ("pk",)
