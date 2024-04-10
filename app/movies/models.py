import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField("name", max_length=255)
    description = models.TextField("description", blank=True, null=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Filmwork(UUIDMixin, TimeStampedMixin):
    class Type(models.TextChoices):
        MOVIE = "movie", _("Movie")
        TV_SHOW = "tv_show", _("TV Show")

    title = models.CharField("title", max_length=255)
    description = models.TextField("description", blank=True, null=True)
    file_path = models.TextField("file_path", blank=True, null=True)
    creation_date = models.DateField("creation_date", null=True, blank=True)
    rating = models.FloatField(
        "rating",
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    type = models.CharField(
        max_length=7,
        choices=Type.choices,
        default=Type.MOVIE,
    )
    genres = models.ManyToManyField(Genre, through="GenreFilmwork")

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = "Кинопроизведение"
        verbose_name_plural = "Кинопроизведения"

    def serialize(self):
        return {
            "id": str(self.id),  # Преобразование UUID в строку
            "title": self.title,
            "description": self.description,
            "creation_date": str(self.creation_date) if self.creation_date else None,
            "rating": float(self.rating) if self.rating is not None else None,
            "type": self.type,
            "genres": [genre.name for genre in self.genres.all()],
        }


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        verbose_name = _("selected_genre")  # 'Выбранный жанр'
        verbose_name_plural = _("selected_genres")  # 'Выбранные жанры'


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField("full_name", max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=["full_name"], name="full_name_idx"),
        ]
        db_table = 'content"."person'
        verbose_name = "Человек"
        verbose_name_plural = "Люди"


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    role = models.TextField("role", null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        # 'Связь человека с кинопроизведением'
        verbose_name = _("person_film_work_relation")
        # 'Связи людей с кинопроизведениями'
        verbose_name_plural = _("person_film_work_relations")
