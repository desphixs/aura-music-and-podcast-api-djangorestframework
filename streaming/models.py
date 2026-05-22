from django.db import models
# settings is imported so we can reference our custom User model via settings.AUTH_USER_MODEL
from django.conf import settings
# post_save is the specific database signal triggered immediately after a model record is saved
from django.db.models.signals import post_save
# receiver is the decorator used to connect our signal handler functions to signals
from django.dispatch import receiver
# MinValueValidator and MaxValueValidator are used to enforce numeric boundaries on integer fields
from django.core.validators import MinValueValidator, MaxValueValidator

from accounts.models import Profile
# The Category model is used to organize podcasts into distinct groups (e.g. Comedy, Tech).
# Think of this as labels on different aisles in a record store.
class Category(models.Model):
    # name is a CharField containing the name of the category.
    # 'unique=True' ensures that we don't accidentally create duplicate categories with the same name.
    name = models.CharField(max_length=100, unique=True)

    # The __str__ method defines the human-readable text representation of a Category object.
    def __str__(self):
        # Returns the name of the category.
        return self.name


# The Podcast model represents a specific podcast show or channel.
# Think of this like a radio show created by a specific host.
class Podcast(models.Model):
    # title is the name of the podcast show.
    title = models.CharField(max_length=255)
    # description contains the background details about what the show is about.
    # We allow blank descriptions and set the default value to an empty string.
    description = models.TextField(blank=True, default='')
    # creator links this podcast show to a specific User.
    # 'on_delete=models.CASCADE' means if the creator's user account is deleted, all their podcasts are deleted too.
    # 'related_name="podcasts"' allows us to query all podcasts created by a user using user.podcasts.all().
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='podcasts'
    )
    # category connects the podcast to a Category model for logical grouping.
    # 'on_delete=models.SET_NULL' means if a Category is deleted, we keep the podcast but clear its category field.
    # 'null=True' and 'blank=True' make this field completely optional.
    # 'related_name="podcasts"' lets us fetch all podcasts in a category via category.podcasts.all().
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='podcasts'
    )
    # created_at automatically records the exact timestamp when the podcast is created.
    created_at = models.DateTimeField(auto_now_add=True)

    # The __str__ method defines the human-readable text representation of a Podcast object.
    def __str__(self):
        # Returns the title of the podcast.
        return self.title


# The Track model represents a single audio file or episode within a specific Podcast.
# Think of this like a single track on an audio album CD.
class Track(models.Model):
    # title is the name of this specific track/episode.
    title = models.CharField(max_length=255)
    # audio_url stores the streaming link pointing to the audio file storage.
    audio_url = models.TextField()
    # duration stores the length of the track in seconds as a text field.
    # We use a CharField to act as a text field as requested by the task requirements.
    duration = models.CharField(
        max_length=50,
        help_text="Duration of the track in seconds (stored as text)"
    )
    # podcast connects this track to its parent Podcast.
    # 'on_delete=models.CASCADE' means if the podcast is deleted, all its tracks are also deleted.
    # 'related_name="tracks"' allows us to access all tracks in a podcast using podcast.tracks.all().
    podcast = models.ForeignKey(
        Podcast,
        on_delete=models.CASCADE,
        related_name='tracks'
    )
    # created_at automatically records the exact timestamp when this track is uploaded.
    created_at = models.DateTimeField(auto_now_add=True)

    # The __str__ method defines the human-readable text representation of a Track object.
    def __str__(self):
        # Returns a string combining the podcast title and the track title.
        return f"{self.podcast.title} - {self.title}"


# The Rating model stores 5-star ratings left by listeners on podcasts.
# Think of this like customers leaving a review score for a service.
class Rating(models.Model):
    # score stores the integer rating.
    # We restrict values to be strictly between 1 and 5 using Django's built-in validator classes.
    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    # user links this rating to the User who submitted it.
    # 'on_delete=models.CASCADE' means if a user is deleted, all their rating records are deleted.
    # 'related_name="ratings"' lets us access all reviews written by a user using user.ratings.all().
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    # podcast connects this rating to the Podcast being reviewed.
    # 'on_delete=models.CASCADE' means if a podcast is deleted, all rating scores on it are also deleted.
    # 'related_name="ratings"' lets us access all rating scores on a podcast using podcast.ratings.all().
    podcast = models.ForeignKey(
        Podcast,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    # created_at automatically records the exact timestamp when the rating is submitted.
    created_at = models.DateTimeField(auto_now_add=True)

    # Meta class allows us to define extra database configurations and constraints.
    class Meta:
        # unique_together forces a composite unique key constraint in our database.
        # This prevents the same user from submitting more than one rating for a single podcast.
        unique_together = ('user', 'podcast')

    # The __str__ method defines the human-readable text representation of a Rating object.
    def __str__(self):
        # Returns a descriptive string showing the reviewer and their score.
        return f"{self.user.email} rated {self.podcast.title} as {self.score}/5"

